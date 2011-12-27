from django.contrib import admin
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Other libs
from mptt.admin import MPTTModelAdmin
from mptt.forms import MPTTAdminForm
from fluent_pages.models import UrlNode
from fluent_pages.forms.fields import RelativeRootPathField


class UrlNodeAdminForm(MPTTAdminForm):
    """
    The admin form for the main fields (the ``UrlNode`` object).
    """

    # Using a separate formfield to display the full URL in the override_url field:
    # - The override_url is stored relative to the URLConf root,
    #   which makes the site easily portable to another path or root.
    # - Users don't have to know or care about this detail.
    #   They only see the absolute external URLs, so make the input reflect that as well.
    override_url = RelativeRootPathField(max_length=300, required=False)


    def __init__(self, *args, **kwargs):
        super(UrlNodeAdminForm, self).__init__(*args, **kwargs)
        # Copy the fields/labels from the model field, to avoid repeating the labels.
        modelfield = [f for f in UrlNode._meta.fields if f.name == 'override_url'][0]
        self.fields['override_url'].label = modelfield.verbose_name
        self.fields['override_url'].help_text = modelfield.help_text


    def clean(self):
        """
        Extend valiation of the form, checking whether the URL is unique.
        Returns all fields which are valid.
        """
        # As of Django 1.3, only valid fields are passed in cleaned_data.
        cleaned_data = super(UrlNodeAdminForm, self).clean()

        # See if the current
        all_objects = UrlNode.objects.all().non_polymorphic()

        if self.instance and self.instance.id:
            # Editing an existing page
            current_id = self.instance.id
            other_objects = all_objects.exclude(id=current_id)
            parent = UrlNode.objects.non_polymorphic().get(pk=current_id).parent
        else:
            # Creating new page!
            parent = cleaned_data['parent']
            other_objects = all_objects

        # If fields are filled in, and still valid, check for unique URL.
        # Determine new URL (note: also done in UrlNode model..)
        if cleaned_data.get('override_url'):
            new_url = cleaned_data['override_url']

            if other_objects.filter(_cached_url=new_url).count():
                self._errors['override_url'] = self.error_class([_('This URL is already taken by an other page.')])
                del cleaned_data['override_url']

        elif cleaned_data.get('slug'):
            new_slug = cleaned_data['slug']
            if parent:
                new_url = '%s%s/' % (parent._cached_url, new_slug)
            else:
                new_url = '/%s/' % new_slug

            if other_objects.filter(_cached_url=new_url).count():
                self._errors['slug'] = self.error_class([_('This slug is already used by an other page at the same level.')])
                del cleaned_data['slug']

        return cleaned_data



class UrlNodeAdmin(MPTTModelAdmin):
    """
    The admin screen for the ``UrlNode`` object.
    """

    # Config list page:
    list_display = ('title', 'status_column', 'modification_date', 'actions_column')
    #list_filter = ('status', 'parent')
    search_fields = ('slug', 'title')
    actions = ['make_published']
    change_list_template = ["admin/fluent_pages/urlnode/change_list.html"]

    # Config add/edit:
    base_form = UrlNodeAdminForm
    prepopulated_fields = { 'slug': ('title',), }
    raw_id_fields = ['parent']
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'status',),
        }),
        (_('Menu structure'), {
            'fields': ('sort_order', 'parent', 'in_navigation'),
            'classes': ('collapse',),
        }),
        (_('Publication settings'), {
            'fields': ('publication_date', 'expire_date', 'override_url'),
            'classes': ('collapse',),
        }),
    )
    radio_fields = {'status': admin.HORIZONTAL}


    class Media:
        css = {
            'screen': ('fluent_pages/admin.css',)
        }


    # ---- Hooking into show/save ----


    def get_form(self, request, obj=None, **kwargs):
        # The django admin validation requires the form to have a 'class Meta: model = ..'
        # attribute, or it will complain that the fields are missing.
        # However, this enforces all derived types to redefine the model too,
        # because they need to explicitly set the model again.
        #
        # Instead, pass the form unchecked here, because the standard ModelForm will just work.
        # If the derived class sets the model explicitly, respect that setting.
        if self.form == UrlNodeAdmin.form:
            kwargs['form'] = self.base_form
        return super(UrlNodeAdmin, self).get_form(request, obj, **kwargs)


    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # Get parent object for breadcrumb
        parent_object = None
        parent_id = request.REQUEST.get('parent')
        if add and parent_id:
            parent_object = UrlNode.objects.non_polymorphic().get(pk=int(parent_id))
        elif change:
            parent_object = obj.parent

        context.update({
            'parent_object': parent_object,
        })

        # And go with standard stuff
        return super(UrlNodeAdmin, self).render_change_form(request, context, add, change, form_url, obj)


    def save_model(self, request, obj, form, change):
        # Automatically store the user in the author field.
        if not change:
            obj.author = request.user
        obj.save()


    # ---- list actions ----

    STATUS_ICONS = (
        (UrlNode.PUBLISHED, 'img/admin/icon-yes.gif'),
        (UrlNode.DRAFT,     'img/admin/icon-unknown.gif'),
    )

    def status_column(self, urlnode):
        status = urlnode.status
        title = [rec[1] for rec in UrlNode.STATUSES if rec[0] == status].pop()
        icon  = [rec[1] for rec in self.STATUS_ICONS  if rec[0] == status].pop()
        return u'<img src="%s%s" width="10" height="10" alt="%s" title="%s" />' % (settings.ADMIN_MEDIA_PREFIX, icon, title, title)

    status_column.allow_tags = True
    status_column.short_description = _('Status')


    def actions_column(self, urlnode):
        return u' '.join(self._actions_column(urlnode))

    actions_column.allow_tags = True
    actions_column.short_description = _('actions')

    def _actions_column(self, urlnode):
        assets_root = settings.STATIC_URL or settings.MEDIA_URL
        actions = []
        actions.append(
            u'<a href="add/?%s=%s" title="%s"><img src="%sfluent_pages/img/admin/page_new.gif" width="16" height="16" alt="%s" /></a>' % (
                self.model._mptt_meta.parent_attr, urlnode.pk, _('Add child'), assets_root, _('Add child'))
            )

        if hasattr(urlnode, 'get_absolute_url') and urlnode.is_published:
            actions.append(
                u'<a href="%s" title="%s" target="_blank"><img src="%sfluent_pages/img/admin/world.gif" width="16" height="16" alt="%s" /></a>' % (
                    urlnode.get_absolute_url(), _('View on site'), assets_root, _('View on site'))
                )
        return actions


    # ---- Custom actions ----

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=UrlNode.PUBLISHED)

        if rows_updated == 1:
            message = "1 page was marked as published."
        else:
            message = "%s pages were marked as published." % rows_updated
        self.message_user(request, message)


    make_published.short_description = _("Mark selected objects as published")
