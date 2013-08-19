"""
A set of base classes, to build custom admin pages, for your page types.
"""
from django.contrib import admin
from fluent_pages.models import Page, PageLayout

# Import trick: make the DefaultPage*Admin available first,
# so the classes imported by .overrides can actually import those from this module already.
from .pageadmin import DefaultPageParentAdmin, DefaultPageChildAdmin, PageAdminForm
from .pagelayoutadmin import PageLayoutAdmin
from .overrides import PageParentAdmin, PageChildAdmin, PageAdmin
from .htmlpageadmin import HtmlPageAdmin


__all__ = (
    'PageParentAdmin', 'DefaultPageParentAdmin',
    'PageAdmin', 'DefaultPageChildAdmin',
    'HtmlPageAdmin',
    'PageLayoutAdmin',
    'PageAdminForm'
)


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(Page, admin_class=PageParentAdmin)
admin.site.register(PageLayout, admin_class=PageLayoutAdmin)
