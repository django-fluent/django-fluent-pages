from django.contrib import admin
from fluent_pages.admin.pageadmin import PageAdmin

class RedirectNodeAdmin(PageAdmin):
    radio_fields = {'redirect_type': admin.VERTICAL}

