from django.contrib import admin
from fluent_pages.admin import PageAdmin

class RedirectNodeAdmin(PageAdmin):
    radio_fields = {'redirect_type': admin.VERTICAL}
    radio_fields.update(PageAdmin.radio_fields)
    readonly_shared_fields = PageAdmin.readonly_shared_fields + ('new_url', 'redirect_type')
