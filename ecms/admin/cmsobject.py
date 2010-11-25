from django.contrib import admin
from django import forms
from django.db import models, transaction
from django.conf.urls.defaults import patterns

# Core objects
from django.http import Http404, HttpResponseRedirect
from django.forms.models import ModelForm, inlineformset_factory
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


class CmsTextItemInline(admin.StackedInline):
    model = CmsTextItem
    extra = 1

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
    list_display = ('title', 'slug', 'status', 'modification_date')
    #list_filter = ('status', 'parent')
    search_fields = ('slug', 'title')
    actions = ['make_published']

    #form = CmsObjectAdminForm
    #inlines = [CmsTextItemInline]

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
            'fields': ('publication_date', 'expire_date', 'parent', 'override_url'),
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
            json = {
                'id': layout.id,
                'key': layout.key,
                'title': layout.title,
                'regions': [{ 'key': r.key, 'title': r.title, 'role': r.role} for r in layout.regions.only('key', 'title', 'role')]
            }
        except CmsLayout.DoesNotExist:
            json = None

        return JsonResponse(json)


    # ---- Hooking into show/save ----

    def save_model(self, request, obj, form, change):
        """Automatically store the user in the author field."""
        if not change:
            obj.author = request.user

        obj.save()


    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, extra_context=None):
        """
        Overwritten entire change view.

        The standard change view made it hard to save custom objects (e.g. CmsPageItem objects).
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

        ModelForm = self.get_form(
            request,
            obj,
            # NOTE: Fields *MUST* be set to None to avoid breaking `django.contrib.admin.options`.
            # ModelAdmin's default get_form() issues a `fields = flatten_fieldsets()` which
            # generates a very abbreviated field list causing KeyErrors during clean() / save()
            fields=None,  # avoids flatten_fieldsets()
        )

        # Generate a formset type for every concrete content type
        # layout: [ (Type, FormSetType), (Type, FormSetType) ]
        #
        # Every pageitem type can override the form, to use. It will fallback to the ItemEditorForm
        # the formfield_callback specifies the FormField object per DB field. curry() prepends args.
        inline_formset_types = [
            (
                PageItemType,
                inlineformset_factory(
                    self.model,
                    PageItemType,
                    extra=1,
                    max_num=1,         # for now it is.
                    fk_name='parent',  # be explicit about the foreign key, so no auto detection is needed.
                    can_delete=False,  # hide delete checkbox
                    form=getattr(PageItemType, 'ecms_item_editor_form', ItemEditorForm),
                    formfield_callback=curry(self.formfield_for_dbfield, request=request)
                )
            ) for PageItemType in [CmsTextItem]  # self.model._get_supported_page_item_types()
        ]

        # Get the forms.
        # Each CmsObject can hold several sub objects of various types.
        # These are all processed as FormSet collections.
        formsets = []
        if request.method == 'POST':
            model_form = ModelForm(request.POST, request.FILES, instance=obj)

            # Get all ECMS inlines
            inline_formsets = [
                FormSetClass(request.POST, request.FILES, instance=obj, prefix=PageItemType.__name__.lower())
                for PageItemType, FormSetClass in inline_formset_types
            ]

            if model_form.is_valid():
                form_validated = True
                new_object = self.save_form(request, model_form, change=True)
            else:
                form_validated = False
                new_object = obj

            # Get all standard admin inlines
            prefixes = {}
            for FormSet in self.get_formsets(request, new_object):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix)
                formsets.append(formset)

            # Store
            if all_valid(inline_formsets+formsets) and form_validated:
                #model_form.save(commit=False)
                model_form.save_m2m()
                for formset in inline_formsets:
                    formset.save()

                #model_form.save(commit=True)
                self.save_model(request, new_object, model_form, change=True)
                for formset in formsets:
                    self.save_formset(request, model_form, formset, change=True)

                # Do the proper redirect
                msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
                if request.POST.has_key("_continue"):
                    self.message_user(request, msg + ' ' + _("You may edit it again below."))
                    return HttpResponseRedirect('.')
                elif request.POST.has_key('_addanother'):
                    self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
                    return HttpResponseRedirect("../add/")
                else:
                    self.message_user(request, msg)
                    return HttpResponseRedirect("../")

        else:
            # Get form and ecms inlines
            model_form = ModelForm(instance=obj)

            # Get all ECMS inlines
            inline_formsets = [
                FormSetClass(instance=obj, prefix=PageItemType.__name__.lower())
                for PageItemType, FormSetClass in inline_formset_types
            ]

            # Get all standard admin inlines
            prefixes = {}
            for FormSet in self.get_formsets(request, obj):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1   # track follow-up number per formset type
                if prefixes[prefix] != 1:
                    prefix = "%s-%d" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix)
                formsets.append(formset)

        # Build admin form around the model form
        # It wraps the form to offer features like fieldsets.
        adminForm = admin.helpers.AdminForm(
            model_form,
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
            inline_admin_formset = admin.helpers.InlineAdminFormSet(inline, formset, fieldsets)
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
            #'errors': admin.helpers.AdminErrorList(adminForm, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})

        return self.render_change_form(request, context, change=True, obj=obj)


    # ---- Custom actions ----

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=CmsObject.PUBLISHED)

        if rows_updated == 1:
            message = "1 page was marked as published."
        else:
            message = "%s pages were marked as published." % rows_updated
        self.message_user(request, message)


    make_published.short_description = _("Mark selected objects as published")
