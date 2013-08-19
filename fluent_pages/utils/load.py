from __future__ import absolute_import
from importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from fluent_pages import appsettings

__all__ = ('import_appsetting_class', 'import_class', 'import_apps_submodule')


def import_appsetting_class(appsetting_name):
    """
    Return the class pointed to be an app setting variable.
    """
    config_value = getattr(appsettings, appsetting_name)
    if config_value is None:
        return None

    return import_class(config_value, appsetting_name)


def import_class(import_path, setting_name):
    """
    Import a class by name.
    """
    mod_name, class_name = import_path.rsplit('.', 1)

    # import module
    try:
        mod = import_module(mod_name)
        cls = getattr(mod, class_name)
    except ImportError, e:
        if mod_name not in str(e):
            raise   # import error is a level deeper.
        else:
            raise ImproperlyConfigured("{0} does not point to an existing class: {1}".format(setting_name, import_path))
    except AttributeError:
        raise ImproperlyConfigured("{0} does not point to an existing class: {1}".format(setting_name, import_path))

    return cls


def import_apps_submodule(submodule):
    """
    Look for a submodule is a series of packages, e.g. ".pagetype_plugins" in all INSTALLED_APPS.
    """
    for app in settings.INSTALLED_APPS:
        try:
            import_module('.' + submodule, app)
        except ImportError, e:
            if submodule not in str(e):
                raise   # import error is a level deeper.
            else:
                pass
