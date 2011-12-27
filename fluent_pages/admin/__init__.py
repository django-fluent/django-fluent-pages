from django.contrib import admin
from fluent_pages.models import UrlNode, Page, CmsLayout
from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin
from fluent_pages.admin.pageadmin import PageAdmin
from fluent_pages.admin.cmslayoutadmin import CmsLayoutAdmin

__all__ = ['CmsObjectAdmin', 'CmsLayoutAdmin']


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(UrlNode, admin_class=UrlNodeAdmin)
admin.site.register(Page, admin_class=PageAdmin)
admin.site.register(CmsLayout, admin_class=CmsLayoutAdmin)
