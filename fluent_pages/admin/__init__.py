from django.contrib import admin
from fluent_pages.models import UrlNode, Page, PageLayout
from fluent_pages.admin.urlnodepolymorphicadmin import UrlNodePolymorphicAdmin
from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin
from fluent_pages.admin.pageadmin import PageAdmin
from fluent_pages.admin.pagelayoutadmin import PageLayoutAdmin

__all__ = ['UrlNodeAdmin', 'PageAdmin', 'PageLayoutAdmin']


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(Page, admin_class=UrlNodePolymorphicAdmin)
admin.site.register(PageLayout, admin_class=PageLayoutAdmin)
