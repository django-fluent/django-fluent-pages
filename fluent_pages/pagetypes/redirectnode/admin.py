from django.contrib import admin
from django.contrib.admin.options import get_ul_class
from django.contrib.admin.widgets import AdminRadioSelect
from fluent_pages.admin import PageAdmin
from django.utils.translation import ugettext_lazy as _


class RedirectNodeAdmin(PageAdmin):
    FIELDSET_REDIRECT = (_('Redirect settings'), {
        'fields': ('new_url', 'redirect_type'),
    })

    # Exclude in_sitemap
    fieldsets = (
        PageAdmin.FIELDSET_GENERAL,
        FIELDSET_REDIRECT,
        PageAdmin.FIELDSET_MENU,
        PageAdmin.FIELDSET_PUBLICATION,
    )

    # Sadly, can't use radio_fields for translatable fields
    #radio_fields = {'redirect_type': admin.VERTICAL}
    #radio_fields.update(PageAdmin.radio_fields)

    def formfield_for_choice_field(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a database Field that has declared choices.
        """
        # If the field is named as a radio_field, use a RadioSelect
        if db_field.name == 'redirect_type':
            kwargs['widget'] = AdminRadioSelect(attrs={'class': get_ul_class(admin.VERTICAL)})
        return db_field.formfield(**kwargs)
