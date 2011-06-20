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

class PluginAlreadyRegistered(Exception):
    pass


class PluginPool(object):
    """
    The central administration of plugins.
    """
    # This is mostly inspired by Django CMS,
    # (c) Django CMS developers, BSD licensed.

    def __init__(self):
        self.plugins = {}
        self.detected = False

    def register(self, plugin):
        """
        Make a plugin known by the CMS.

        If a plugin is already registered, this will raise PluginAlreadyRegistered.
        """
        # While plugins can be easily detected via EcmsPlugin.__subclasses__(),
        # this is A) magic, and B) less explicit. Having to do an explicit register
        # ensures future compatibility with other API's like reversion.
        assert issubclass(plugin, EcmsPlugin), "The plugin must inherit from `CMSPluginBase`"
        plugin_name = plugin.__name__
        if plugin_name in self.plugins:
            raise PluginAlreadyRegistered("[%s] a plugin with this name is already registered" % plugin_name)
        self.plugins[plugin_name] = plugin


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

        for app in settings.INSTALLED_APPS:
            try:
                import_module('.ecms_plugins', app)
            except ImportError, e:
                if "ecms_plugins" not in str(e):
                    raise   # import error is a level deeper.
                else:
                    pass

        self.detected = True

plugin_pool = PluginPool()
