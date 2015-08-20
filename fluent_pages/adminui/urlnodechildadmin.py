from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _, ugettext
from mptt.forms import MPTTAdminForm
from parler import is_multilingual_project
from polymorphic_tree.admin import PolymorphicMPTTChildModelAdmin
from fluent_pages import appsettings
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm, TranslatedField
from slug_preview.forms import SlugPreviewFormMixin
from fluent_pages.models import UrlNode, UrlNode_Translation
from fluent_pages.forms.fields import RelativeRootPathField
from fluent_utils.dry.admin import MultiSiteAdminMixin
import mptt


class UrlNodeAdminForm(MPTTAdminForm, SlugPreviewFormMixin, TranslatableModelForm):
    """
    The admin form for the main fields (the ``UrlNode`` object).
    """
    # Using a separate formfield to display the full URL in the override_url field:
    # - The override_url is stored relative to the URLConf root,
    #   which makes the site easily portable to another path or root.
    # - Users don't have to know or care about this detail.
    #   They only see the absolute external URLs, so make the input reflect that as well.
    title = TranslatedField()
    slug = TranslatedField()
    override_url = TranslatedField(form_class=RelativeRootPathField)

    def __init__(self, *args, **kwargs):
        if 'parent' not in self.base_fields and mptt.VERSION[:2] == (0, 6):
            # Skip bug in django-mptt 0.6.0
            # https://github.com/django-mptt/django-mptt/issues/275
            TranslatableModelForm.__init__(self, *args, **kwargs)
        else:
            super(UrlNodeAdminForm, self).__init__(*args, **kwargs)

        if 'override_url' in self.fields:
            self.fields['override_url'].language_code = self.language_code

        # When the is_sitemap field is exposed, make sure it has the right default.
        # This can't be set on the model level, because the default depends on the page type.
        if 'in_sitemaps' in self.fields and not self.instance.pk:
            self.fields['in_sitemaps'].initial = self.instance.plugin.default_in_sitemaps

    def clean(self):
        """
        Extend valiation of the form, checking whether the URL is unique.
        Returns all fields which are valid.
        """
        # As of Django 1.3, only valid fields are passed in cleaned_data.
        cleaned_data = super(UrlNodeAdminForm, self).clean()

        # See if the current URLs don't overlap.
        all_nodes = UrlNode.objects.all()
        all_translations = UrlNode_Translation.objects.all()
        if appsettings.FLUENT_PAGES_FILTER_SITE_ID:
            site_id = (self.instance is not None and self.instance.parent_site_id) or settings.SITE_ID
            all_nodes = all_nodes.filter(parent_site=site_id)
            all_translations = all_translations.filter(master__parent_site=site_id)

        if self.instance and self.instance.id:
            # Editing an existing page
            current_id = self.instance.id
            other_nodes = all_nodes.exclude(id=current_id)
            other_translations = all_translations.exclude(master_id=current_id)

            # Get original unmodified parent value.
            try:
                parent = UrlNode.objects.non_polymorphic().get(children__pk=current_id)
            except UrlNode.DoesNotExist:
                parent = None
        else:
            # Creating new page!
            parent = cleaned_data['parent']
            other_nodes = all_nodes
            other_translations = all_translations

        # Unique check for the `key` field.
        if cleaned_data.get('key'):
            if other_nodes.filter(key=cleaned_data['key']).count():
                self._errors['key'] = self.error_class([_('This identifier is already used by an other page.')])
                del cleaned_data['key']

        # If fields are filled in, and still valid, check for unique URL.
        # Determine new URL (note: also done in UrlNode model..)
        if cleaned_data.get('override_url'):
            new_url = cleaned_data['override_url']

            if other_translations.filter(_cached_url=new_url).count():
                self._errors['override_url'] = self.error_class([_('This URL is already taken by an other page.')])
                del cleaned_data['override_url']

        elif cleaned_data.get('slug'):
            new_slug = cleaned_data['slug']
            if parent:
                new_url = '%s%s/' % (parent._cached_url, new_slug)
            else:
                new_url = '/%s/' % new_slug

            if other_translations.filter(_cached_url=new_url).count():
                self._errors['slug'] = self.error_class([_('This slug is already used by an other page at the same level.')])
                del cleaned_data['slug']

        return cleaned_data


class UrlNodeChildAdmin(MultiSiteAdminMixin, PolymorphicMPTTChildModelAdmin, TranslatableAdmin):
    """
    The internal machinery
    The admin screen for the ``UrlNode`` objects.
    """
    filter_site = appsettings.FLUENT_PAGES_FILTER_SITE_ID
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
        'fields': ('publication_date', 'publication_end_date', 'override_url',),
        'classes': ('collapse',),
    })
    if appsettings.FLUENT_PAGES_KEY_CHOICES:
        FIELDSET_PUBLICATION[1]['fields'] += ('key',)

    #: The fieldsets to display.
    #: Any missing fields will be displayed in a separate section (named :attr:`extra_fieldset_title`) automatically.
    base_fieldsets = (
        FIELDSET_GENERAL,
        FIELDSET_MENU,
        FIELDSET_PUBLICATION,
    )

    # Config add/edit page:
    raw_id_fields = ('parent',)
    radio_fields = {'status': admin.HORIZONTAL}
    readonly_shared_fields = ('status', 'in_navigation', 'parent', 'publication_date', 'publication_end_date',)

    if not appsettings.FLUENT_PAGES_KEY_CHOICES:
        # Not passing exclude= to get_form() because that overrides get_readonly_fields().
        # Instead, declare it here to be read by get_form()
        exclude = ('key',)
    else:
        exclude = ()

    # The static prepopulated_fields attribute is validated and fails.
    # The object function does work, and django-parler provides the media
    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('title',)
        }

    # NOTE: list page is configured in UrlNodeParentAdmin
    # as that class is used for the real admin screen.
    # This class is only a base class for the custom pagetype plugins.

    def get_readonly_fields(self, request, obj=None):
        """
        Determine which fields are readonly.
        This includes the shared fields if the user has no permission to change them.
        """
        fields = super(UrlNodeChildAdmin, self).get_readonly_fields(request, obj)
        if obj is not None:
            # Edit screen
            if len(obj.get_available_languages()) >= 2 \
            and not self.has_change_shared_fields_permission(request, obj):
                # This page is translated in multiple languages,
                # language team is only allowed to update their own language.
                fields += self.readonly_shared_fields

        # The override_url is an advanced property that should typically only be set
        # once for the homepage (set to '/') so avoid that other users can change it.
        if not self.has_change_override_url_permission(request, obj):
            fields += ('override_url',)

        return fields

    def has_change_shared_fields_permission(self, request, obj=None):
        """
        Whether the user can change the page layout.
        """
        opts = self.opts
        codename = '{0}.change_shared_fields_urlnode'.format(opts.app_label)
        return request.user.has_perm(codename, obj=obj)

    def has_change_override_url_permission(self, request, obj=None):
        """
        Whether the user can change the page layout.
        """
        opts = self.opts
        codename = '{0}.change_override_url_urlnode'.format(opts.app_label)
        return request.user.has_perm(codename, obj=obj)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Allow formfield_overrides to contain field names too.
        """
        overrides = self.formfield_overrides.get(db_field.name)
        if overrides:
            kwargs.update(overrides)

        return super(UrlNodeChildAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def save_model(self, request, obj, form, change):
        # Automatically store the user in the author field.
        if not change:
            obj.author = request.user

            # The in_sitemaps field is only exposed in the HtmlPageAdmin and up.
            # Hence, some object types don't have an "in_sitemaps" option in their form.
            # Use the default in those cases.
            if 'in_sitemaps' not in form.fields:
                obj.in_sitemaps = obj.plugin.default_in_sitemaps

        super(UrlNodeChildAdmin, self).save_model(request, obj, form, change)
