import re

from django.apps import AppConfig
from fluent_utils.load import import_module_or_none


class FluentPagesConfig(AppConfig):
    name = "fluent_pages"
    verbose_name = "Fluent Pages"

    def ready(self):
        _register_subclass_types()


def _register_subclass_types():
    """
    See if any page type plugin uses the old registration system, and register that
    Previously django-polymorphic registered all subclasses internally.
    Nowadays, all subclasses should just be registered in the regular admin.
    """
    from django.contrib import admin

    RE_PLUGIN_MODULE = re.compile(r"\.page_type_plugins\b.*$")

    from fluent_pages.extensions import page_type_pool

    for plugin in page_type_pool.get_plugins():
        if plugin.model in admin.site._registry:
            continue

        # First try to perform an admin file import, it may register itself.
        admin_path = RE_PLUGIN_MODULE.sub(".admin", plugin.__module__)
        module = import_module_or_none(admin_path)
        if module is not None and plugin.model in admin.site._registry:
            continue

        # Register the admin, since the plugin didn't do this.
        if getattr(plugin, "model_admin", None):
            admin.site.register(plugin.model, plugin.model_admin)
