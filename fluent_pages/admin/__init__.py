"""
The admin site registration.

This is separate from the admin classes, so those can be imported freely without invoking ``admin.site.register()``.
The admin site registration is only possible in Django 1.7 once all models are loaded.
"""
import re
from django.contrib import admin
from importlib import import_module

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
    RE_PLUGIN_MODULE = re.compile(r'\.page_type_plugins\b.*$')

    from fluent_pages.extensions import page_type_pool
    for plugin in page_type_pool.get_plugins():
        if plugin.model in admin.site._registry:
            continue

        # First try to perform an admin file import, it may register itself.
        admin_path = RE_PLUGIN_MODULE.sub('.admin', plugin.__module__)
        try:
            import_module(admin_path)
        except ImportError:
            pass
        else:
            if plugin.model in admin.site._registry:
                continue

        # Register the admin, since the plugin didn't do this.
        if getattr(plugin, 'model_admin', None):
            admin.site.register(plugin.model, plugin.model_admin)


# Register the models with the admin site
_register_subclass_types()
admin.site.register(Page, admin_class=PageParentAdmin)
admin.site.register(PageLayout, admin_class=PageLayoutAdmin)
