from django.contrib import admin
from fluent_pages.admin import PageAdmin
from django.utils.translation import ugettext_lazy as _

class RedirectNodeAdmin(PageAdmin):
    radio_fields = {'redirect_type': admin.VERTICAL}
    radio_fields.update(PageAdmin.radio_fields)
    readonly_shared_fields = PageAdmin.readonly_shared_fields + ('new_url', 'redirect_type')

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
