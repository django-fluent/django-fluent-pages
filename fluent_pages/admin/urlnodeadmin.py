from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.forms import MPTTAdminForm
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin
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
        modelfield = UrlNode._meta.get_field_by_name('override_url')[0]
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



class UrlNodeAdmin(PolymorphicMPTTChildModelAdmin):
    """
    The internal machinery
    The admin screen for the ``UrlNode`` objects.
    """
    base_model = UrlNode
    base_form = UrlNodeAdminForm


    # Expose fieldsets for subclasses to reuse
    #: The general fieldset to display
    FIELDSET_GENERAL = (None, {
        'fields': ('title', 'slug', 'status', 'in_navigation'),
    })
    #: The menu fieldset
    FIELDSET_MENU = (_('Menu structure'), {
        'fields': ('parent',),
        'classes': ('collapse',),
    })
    #: The publication fields.
    FIELDSET_PUBLICATION = (_('Publication settings'), {
        'fields': ('publication_date', 'publication_end_date', 'override_url'),
        'classes': ('collapse',),
    })

    #: The fieldsets to display.
    #: Any missing fields will be displayed in a separate section (named :attr:`extra_fieldset_title`) automatically.
    base_fieldsets = (
        FIELDSET_GENERAL,
        FIELDSET_MENU,
        FIELDSET_PUBLICATION,
    )

    # Config add/edit page:
    prepopulated_fields = { 'slug': ('title',), }
    raw_id_fields = ('parent',)
    radio_fields = {'status': admin.HORIZONTAL}

    # NOTE: list page is configured in UrlNodePolymorphicAdmin
    # as that class is used for the real admin screen.
    # This class is only a base class for the custom pagetype plugins.


    def save_model(self, request, obj, form, change):
        # Automatically store the user in the author field.
        if not change:
            obj.author = request.user
        obj.save()
