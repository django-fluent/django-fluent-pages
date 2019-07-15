"""
The admin site registration.

This is separate from the admin classes, so those can be imported freely without invoking ``admin.site.register()``.
The admin site registration is only possible in Django 1.7 once all models are loaded.
"""
from django.contrib import admin

# Leaving all old imports here
# However, when using FLUENT_PAGES_PARENT_ADMIN_MIXIN / FLUENT_PAGES_CHILD_ADMIN_MIXIN
# you can easily get circular import errors. Instead, import the classes from the adminui package.
from fluent_pages.adminui import (
    DefaultPageChildAdmin,
    DefaultPageParentAdmin,
    HtmlPageAdmin,
    PageAdmin,
    PageAdminForm,
    PageLayoutAdmin,
    PageParentAdmin,
)
from fluent_pages.models import Page, PageLayout

# Register the models with the admin site
admin.site.register(Page, admin_class=PageParentAdmin)
admin.site.register(PageLayout, admin_class=PageLayoutAdmin)
