from django.contrib import admin
from fluent_pages.admin.pageadmin import PageAdmin

class RedirectNodeAdmin(PageAdmin):
    radio_fields = {'redirect_type': admin.VERTICAL}

    # TODO: enforce parent radio fields.
    radio_fields.update(PageAdmin.radio_fields)