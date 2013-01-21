from django.contrib import admin
from fluent_pages.admin import PageAdmin

class RedirectNodeAdmin(PageAdmin):
    radio_fields = {'redirect_type': admin.VERTICAL}
    radio_fields.update(PageAdmin.radio_fields)
