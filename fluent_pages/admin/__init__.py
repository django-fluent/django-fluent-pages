"""
A set of base classes, to build custom admin pages, for your page types.
"""
from django.contrib import admin
from fluent_pages.models import Page, PageLayout
from fluent_pages.admin.urlnodepolymorphicadmin import UrlNodePolymorphicAdmin
from fluent_pages.admin.pageadmin import PageAdmin, HtmlPageAdmin, PageAdminForm
from fluent_pages.admin.pagelayoutadmin import PageLayoutAdmin

__all__ = ['PageAdmin', 'HtmlPageAdmin', 'PageLayoutAdmin', 'PageAdminForm']


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(Page, admin_class=UrlNodePolymorphicAdmin)
admin.site.register(PageLayout, admin_class=PageLayoutAdmin)
