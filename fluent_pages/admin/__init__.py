"""
The admin site registration.

This is separate from the admin classes, so those can be imported freely without invoking ``admin.site.register()``.
The admin site registration is only possible in Django 1.7 once all models are loaded.
"""
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from fluent_pages.models import Page, PageLayout

# Leaving all old imports here
# However, when using FLUENT_PAGES_PARENT_ADMIN_MIXIN / FLUENT_PAGES_CHILD_ADMIN_MIXIN
# you can easily get circular import errors. Instead, import the classes from the adminui package.
from fluent_pages.adminui import (
    PageParentAdmin, DefaultPageParentAdmin,
    PageAdmin, DefaultPageChildAdmin,
    HtmlPageAdmin,
    PageLayoutAdmin,
    PageAdminForm,
)


# -------- Model registration --------

def _register_subclass_types():
    """
    See if any page type plugin uses the old registration system, and register that
    Previously django-polymorphic registered all subclasses internally.
    Nowadays, all subclasses should just be registered in the regular admin.
    """
    from fluent_pages.extensions import page_type_pool
    for plugin in page_type_pool.get_plugins():
        try:
            if getattr(plugin, 'model_admin', None):
                admin.site.register(plugin.model, plugin.model_admin)
        except AlreadyRegistered:
            pass


# Register the models with the admin site
_register_subclass_types()
admin.site.register(Page, admin_class=PageParentAdmin)
admin.site.register(PageLayout, admin_class=PageLayoutAdmin)
