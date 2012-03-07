from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from mptt.forms import MPTTAdminForm
from fluent_pages.utils.polymorphicadmin import PolymorphedModelAdmin
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



class UrlNodeAdmin(PolymorphedModelAdmin, MPTTModelAdmin):
    """
    The internal machinery
    The admin screen for the ``UrlNode`` objects.
    """
    base_model = UrlNode
    base_form = UrlNodeAdminForm


    # Expose fieldsets for subclasses to reuse
    FIELDSET_GENERAL = (None, {
        'fields': ('title', 'slug', 'status',),
    })
    FIELDSET_MENU = (_('Menu structure'), {
        'fields': ('sort_order', 'parent', 'in_navigation'),
        'classes': ('collapse',),
    })
    FIELDSET_PUBLICATION = (_('Publication settings'), {
        'fields': ('publication_date', 'expire_date', 'override_url'),
        'classes': ('collapse',),
    })

    base_fieldsets = (
        FIELDSET_GENERAL,
        FIELDSET_MENU,
        FIELDSET_PUBLICATION,
    )

    # Config add/edit page:
    prepopulated_fields = { 'slug': ('title',), }
    raw_id_fields = ['parent']
    radio_fields = {'status': admin.HORIZONTAL}

    # NOTE: list page is configured in UrlNodePolymorphicAdmin
    # as that class is used for the real admin screen.
    # This class is only a base class for the custom pagetype plugins.


    class Media:
        css = {
            'screen': ('fluent_pages/admin.css',)
        }


    def save_model(self, request, obj, form, change):
        # Automatically store the user in the author field.
        if not change:
            obj.author = request.user
        obj.save()


    # ---- Pass parent_object to templates ----

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # Get parent object for breadcrumb
        parent_object = None
        parent_id = request.REQUEST.get('parent')
        if add and parent_id:
            parent_object = UrlNode.objects.get(pk=int(parent_id))  # is polymorphic
        elif change:
            parent_object = obj.parent

        # Improve the breadcrumb
        context.update({
            'parent_object': parent_object,
        })

        return super(UrlNodeAdmin, self).render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)


    def delete_view(self, request, object_id, context=None):
        # Get parent object for breadcrumb
        parent_object = None
        try:
            parent_pk = UrlNode.objects.non_polymorphic().values('parent').filter(pk=int(object_id))
            parent_object = UrlNode.objects.get(pk=parent_pk)
        except UrlNode.DoesNotExist:
            pass

        # Improve the breadcrumb
        extra_context = {
            'parent_object': parent_object,
        }
        extra_context.update(context or {})

        return super(UrlNodeAdmin, self).delete_view(request, object_id, extra_context)
