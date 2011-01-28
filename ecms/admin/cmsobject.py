from django.contrib import admin
from django import forms
from django.db import models, transaction
from django.conf import settings
from django.conf.urls.defaults import patterns

# Core objects
from django.http import Http404
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied

# Many small imports
from django.contrib.admin.util import unquote
from django.forms.formsets import all_valid
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.functional import curry
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Other libs
from mptt.admin import MPTTModelAdmin   # mptt 0.4
from ecms.models import CmsObject, CmsTextItem, CmsLayout
from vdboor.ajax import JsonResponse

csrf_protect_m = method_decorator(csrf_protect)


class CmsObjectAdminForm(forms.ModelForm):
    """
    The admin form for the main fields (the ``CmsObject`` object).
    """
    class Meta:
        model = CmsObject

    def clean(self):
        """
        Extend valiation of the form, checking whether the URL is unique.
        Returns all fields which are valid.
        """
        cleaned_data = super(CmsObjectAdminForm, self).clean()

        # See if the current
        current_id = None
        other_objects = CmsObject.objects.all()

        if 'id' in self.initial:
            # Editing an existing page
            current_id = self.initial['id']
            other_objects = other_objects.exclude(id=current_id)
            parent = CmsObject.objects.get(pk=current_id).parent
        else:
            # Creating new page!
            parent = cleaned_data['parent']

        # If fields are filled in, and still valid, check for unique URL.
        # Determine new URL (note: also done in CmsObject model..)
        if cleaned_data['override_url']:
            new_url = cleaned_data['override_url']

            if other_objects.filter(_cached_url=new_url).count():
                self._errors['override_url'] = self.error_class([_('This URL is already taken by an other page.')])
                del cleaned_data['override_url']

        elif cleaned_data['slug']:
            new_slug = cleaned_data['slug']
            if parent:
                new_url = '%s%s/' % (parent._cached_url, new_slug)
            else:
                new_url = '/%s/' % new_slug

            if other_objects.filter(_cached_url=new_url).count():
                self._errors['slug'] = self.error_class([_('This slug is already used by an other page at the same level.')])
                del cleaned_data['slug']

        return cleaned_data


class ItemEditorForm(forms.ModelForm):
    """
    The base form for custom pageitem types.
    """
    region = forms.CharField(widget=forms.HiddenInput(), required=False)
    ordering = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    pass


class CmsObjectAdmin(MPTTModelAdmin):
    """
    The admin screen for the ``CmsObject`` object, with lots of customisations.
    """

    # Config list page:
    list_display = ('title', 'slug', 'status', 'modification_date', 'actions_column')
    #list_filter = ('status', 'parent')
    search_fields = ('slug', 'title')
    actions = ['make_published']

    # Configure edit page:
    form = CmsObjectAdminForm
    change_form_template = ["admin/ecms/cmsobject/cmsobject_editor.html",
                            "admin/ecms/cmsobject_editor.html",
                            ]

    # Config add/edit:
    prepopulated_fields = { 'slug': ('title',), }
    raw_id_fields = ['parent']
    fieldsets = (
        (None, {
            'fields': ('title','status','layout'),
        }),
        (_('SEO settings'), {
            'fields': ('slug', 'keywords', 'description'),
            #'classes': ('collapse',),
        }),
        (_('Publication settings'), {
            'fields': ('publication_date', 'expire_date', 'parent', 'sort_order', 'override_url'),
            #'classes': ('collapse',),
        }),
    )
    radio_fields = {'status': admin.HORIZONTAL}



    # ---- Extra Ajax views ----


    def get_urls(self):
        """
        Introduce more urls
        """
        urls = super(CmsObjectAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^get_layout/(?P<id>\d+)/$', self.admin_site.admin_view(self.get_layout_view))
        )
        return my_urls + urls


    def get_layout_view(self, request, id):
        """
        Return the metadata about a layout
        """
        try:
            layout = CmsLayout.objects.get(pk=id)
        except CmsLayout.DoesNotExist:
            return JsonResponse(None)

        json = {
            'id': layout.id,
            'key': layout.key,
            'title': layout.title,
            'regions': [{ 'key': r.key, 'title': r.title, 'role': r.role} for r in layout.regions.only('key', 'title', 'role')]
        }

        return JsonResponse(json)


    # ---- Hooking into show/save ----

    def save_model(self, request, obj, form, change):
        """Automatically store the user in the author field."""
        if not change:
            obj.author = request.user

        # Set default values for hidden fields.
        obj.in_navigation = True

        obj.save()


    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        """
        Overwritten entire 'add' view.

        This function complements ``change_view`` to save custom objects (e.g. ``CmsPageItem`` objects).
        """
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        # NOTE: Fields *MUST* be set to None to avoid breaking `django.contrib.admin.options`.
        # ModelAdmin's default get_form() issues a `fields = flatten_fieldsets()` which
        # generates a very abbreviated field list causing KeyErrors during clean() / save()

        ModelForm = self.get_form(request, fields=None)  # see note in change_view about fields=None.
        inline_formset_types = self._get_inline_formset_types(request)

        # Each CmsObject can hold several sub objects of various types.
        # These are all processed as FormSet collections.

        # Get the forms + FormSets per content type.
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)

            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                form_validated = True
            else:
                new_object = self.model()
                form_validated = False

            # Get all ECMS inlines
            inline_formsets = [
                FormSetClass(request.POST, request.FILES, instance=new_object, prefix=PageItemType.__name__.lower())
                for PageItemType, FormSetClass in inline_formset_types
            ]

            # Get all standard admin inlines
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new=request.POST.has_key("_saveasnew"),
                                  prefix=prefix, queryset=inline.queryset(request))
                formsets.append(formset)

            # Store
            if all_valid(formsets) and form_validated:
                form.save_m2m()
                self.save_model(request, new_object, form, change=False)
                for formset in inline_formsets:
                    formset.save()

                for formset in formsets:
                    self.save_formset(request, form, formset, change=False)

                # Do the proper redirect
                self.log_addition(request, new_object)
                return self.response_add(request, new_object)

        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")

            # The first page becomes the homepage by default.
            if not CmsObject.objects.count():
                initial['override_url'] = '/'

            # Get form and ecms inlines
            form = ModelForm(initial=initial)
            dummy_object = self.model()

            # Get all ECMS inlines
            inline_formsets = [
                FormSetClass(instance=dummy_object, prefix=PageItemType.__name__.lower())
                for PageItemType, FormSetClass in inline_formset_types
            ]

            # Get all standard admin inlines
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request),
                                       self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1   # track follow-up number per formset type
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=dummy_object, prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)

        # Build admin form around the normal model form
        # It wraps the form to offer features like fieldsets.
        adminForm = admin.helpers.AdminForm(
            form,
            list(self.get_fieldsets(request)),
            self.prepopulated_fields,
            self.get_readonly_fields(request),
            model_admin=self
        )
        media = self.media + adminForm.media

        # Get the standard admin inlines
        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            inline_admin_formset = admin.helpers.InlineAdminFormSet(inline, formset, fieldsets, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'media': mark_safe(media),
            'inline_ecms_formsets': inline_formsets,
            'inline_admin_formsets': inline_admin_formsets,
            #'errors': helpers.AdminErrorList(form, formsets),  # exposed in standard change_view, not here.
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})

        return self.render_change_form(request, context, form_url=form_url, add=True)


    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, extra_context=None):
        """
        Overwritten entire 'change' view.

        The standard change view made it hard to save custom objects (e.g. ``CmsPageItem`` objects).
        """
        model = self.model
        opts = model._meta

        # This block of code is largely inspired and based on FeinCMS
        # (c) Matthias Kestenholz, BSD licensed

        # Get the object
        obj = self.get_object(request, unquote(object_id))
        if not self.has_change_permission(request, obj):
            raise PermissionDenied
        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        ModelForm = self.get_form(request, obj, fields=None)  # see add_view for note about fields=None, it prevents errors during clean() / save()
        inline_formset_types = self._get_inline_formset_types(request, instance=obj)

        # Get the forms + FormSets per content type.
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)

            if form.is_valid():
                new_object = self.save_form(request, form, change=True)
                form_validated = True
            else:
                new_object = obj
                form_validated = False

            # Get all ECMS inlines
            inline_formsets = [
                FormSetClass(request.POST, request.FILES, instance=obj, prefix=PageItemType.__name__.lower())
                for PageItemType, FormSetClass in inline_formset_types
            ]

            # Get all standard admin inlines
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, new_object),
                                       self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1   # track follow-up number per formset type
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix,
                                  queryset=inline.queryset(request))

                formsets.append(formset)

            # Store
            if all_valid(inline_formsets+formsets) and form_validated:
                form.save_m2m()
                for formset in inline_formsets:
                    formset.save()

                self.save_model(request, new_object, form, change=True)
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                # Do the proper redirect
                change_message = self.construct_change_message(request, form, formsets+inline_formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        else:
            # Get form and ecms inlines
            form = ModelForm(instance=obj)

            # Get all ECMS inlines
            inline_formsets = [
                FormSetClass(instance=obj, prefix=PageItemType.__name__.lower())
                for PageItemType, FormSetClass in inline_formset_types
            ]

            # Get all standard admin inlines
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, obj),
                                       self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1   # track follow-up number per formset type
                if prefixes[prefix] != 1:
                    prefix = "%s-%d" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)

        # Build admin form around the normal model form
        # It wraps the form to offer features like fieldsets.
        adminForm = admin.helpers.AdminForm(
            form,
            list(self.get_fieldsets(request)),
            self.prepopulated_fields,
            self.get_readonly_fields(request),
            model_admin=self
        )
        media = self.media + adminForm.media

        # Get the standard admin inlines
        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly  = list(inline.get_readonly_fields(request, obj))
            inline_admin_formset = admin.helpers.InlineAdminFormSet(inline, formset, fieldsets, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': mark_safe(media),
            'inline_ecms_formsets': inline_formsets,
            'inline_admin_formsets': inline_admin_formsets,
            #'errors': admin.helpers.AdminErrorList(adminForm, formsets),  # exposed in standard change_view, not here.
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})

        return self.render_change_form(request, context, change=True, obj=obj)


    def _get_inline_formset_types(self, request, instance=None):
        """
        Generate a formset type for every concrete content type
        returns: [ (Type, FormSetType), (Type, FormSetType) ]

        Every pageitem type can override the form, to use. It will fallback to the ItemEditorForm
        the formfield_callback specifies the FormField object per DB field. curry() prepends args.
        """
        return [
            ( # Tuple:
                PageItemType,
                inlineformset_factory(
                    self.model,        # Parent model
                    PageItemType,      # Child model
                    extra=1,
                    max_num=1,         # for now it is.
                    fk_name='parent',  # be explicit about the foreign key, so no auto detection is needed.
                    can_delete=False,  # hide delete checkbox

                    # The form is either an ItemEditorForm, or custom defined.
                    form=getattr(PageItemType, 'ecms_item_editor_form', ItemEditorForm),
                    formfield_callback=curry(self.formfield_for_dbfield, request=request)
                )
            ) for PageItemType in [CmsTextItem]  # self.model._get_supported_page_item_types()
        ]


    # ---- list actions ----

    def actions_column(self, page):
        return u' '.join(self._actions_column(page))

    actions_column.allow_tags = True
    actions_column.short_description = _('actions')

    def _actions_column(self, obj):
        actions = []
        actions.insert(0,
            u'<a href="add/?%s=%s" title="%s"><img src="%simg/admin/icon_addlink.gif" alt="%s" /></a>' % (
                self.model._mptt_meta.parent_attr,
                obj.pk,
                _('Add child'),
                settings.ADMIN_MEDIA_PREFIX,
                _('Add child')))

        if hasattr(obj, 'get_absolute_url'):
            actions.insert(0,
                u'<a href="%s" title="%s" target="_blank"><img src="%simg/admin/selector-search.gif" alt="%s" /></a>' % (
                    obj.get_absolute_url(),
                    _('View on site'),
                    settings.ADMIN_MEDIA_PREFIX,
                    _('View on site')))
        return actions


    # ---- Custom actions ----

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=CmsObject.PUBLISHED)

        if rows_updated == 1:
            message = "1 page was marked as published."
        else:
            message = "%s pages were marked as published." % rows_updated
        self.message_user(request, message)


    make_published.short_description = _("Mark selected objects as published")
