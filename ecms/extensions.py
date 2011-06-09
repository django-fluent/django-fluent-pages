"""
Special classes to extend the CMS, e.g. plugins.
"""
from django.conf import settings
from django import forms
from django.utils.importlib import import_module
from ecms.models import CmsPageItem


class CmsPageItemForm(forms.ModelForm):
    """
    The base form for custom pageitem types.
    """
    region = forms.CharField(widget=forms.HiddenInput(), required=False)
    sort_order = forms.IntegerField(widget=forms.HiddenInput(), initial=1)


class EcmsPlugin(object):
    """
    The base class for a plugin, defining the settings.
    """

    # Settings to override
    model = CmsPageItem
    admin_form = CmsPageItemForm
    admin_form_template = "admin/ecms/cmspageitem/admin_form.html"



# -------- API to access plugins --------


def get_plugin_classes():
    """
    Return the list of all plugin classes which are loaded.
    """
    _import_plugins()
    return EcmsPlugin.__subclasses__()


_loaded_plugins = False

def _import_plugins():
    """
    Internal function, ensure all plugin packages are imported.
    """
    global _loaded_plugins
    if _loaded_plugins:
        return

    for app in settings.INSTALLED_APPS:
        try:
            import_module('.ecms_plugins', app)
        except ImportError, e:
            if "ecms_plugins" not in e.message:
                raise   # import error is a level deeper.
            else:
                pass

    _loaded_plugins = True
