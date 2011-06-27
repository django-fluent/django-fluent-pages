"""
Special classes to extend the CMS; e.g. plugins.

The extension mechanism is provided for projects that benefit
from a tighter integration then the Django URLconf can provide.
"""
from django.conf import settings
from django import forms
from django.utils.importlib import import_module
from ecms.models import CmsPageItem

# The API uses a registration system.
# While plugins can be easily detected via ``__subclasses__()``, this is more magic and less explicit.
# Having to do an explicit register ensures future compatibility with other API's like reversion.
#
# This mechanism is mostly inspired by Django CMS,
# which nice job at defining a clear extension model.
# (c) Django CMS developers, BSD licensed.


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


# -------- Some utils --------

def _import_app_submodules(submodule):
    """
    Look for a submodule is a series of packages, e.g. ".ecms_plugins" in all INSTALLED_APPS.
    """
    for app in settings.INSTALLED_APPS:
        try:
            import_module('.' + submodule, app)
        except ImportError, e:
            if submodule not in str(e):
                raise   # import error is a level deeper.
            else:
                pass


# -------- API to access plugins --------

class PluginAlreadyRegistered(Exception):
    pass


class PluginPool(object):
    """
    The central administration of plugins.
    """

    def __init__(self):
        self.plugins = {}
        self.detected = False

    def register(self, plugin):
        """
        Make a plugin known by the CMS.

        If a plugin is already registered, this will raise PluginAlreadyRegistered.
        """
        assert issubclass(plugin, EcmsPlugin), "The plugin must inherit from `CMSPluginBase`"
        name = plugin.__name__
        if name in self.plugins:
            raise PluginAlreadyRegistered("[%s] a plugin with this name is already registered" % name)
        self.plugins[name] = plugin


    def get_plugin_classes(self):
        """
        Return the list of all plugin classes which are loaded.
        """
        self._import_plugins()
        return self.plugins.values()


    def get_page_item_classes(self):
        """
        Return all page item models which are exposed by plugins.
        """
        self._import_plugins()
        return [plugin.model for plugin in self.plugins.values()]


    def _import_plugins(self):
        """
        Internal function, ensure all plugin packages are imported.
        """
        if self.detected:
            return
        _import_app_submodules("ecms_plugins")
        self.detected = True

plugin_pool = PluginPool()
