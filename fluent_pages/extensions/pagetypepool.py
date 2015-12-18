"""
Internal module for the plugin system,
the API is exposed via __init__.py
"""
from future.builtins import object, int
from threading import Lock
from django.contrib.contenttypes.models import ContentType
from fluent_pages.models import UrlNode
from fluent_utils.load import import_apps_submodule
from .pagetypebase import PageTypePlugin
from six import itervalues, iteritems


__all__ = (
    'PageTypeAlreadyRegistered', 'PageTypeNotFound', 'PageTypePool', 'page_type_pool'
)


class PageTypeAlreadyRegistered(Exception):
    """
    Raised when attempting to register a plugin twice.
    """
    pass


class PageTypeNotFound(Exception):
    """
    Raised when the plugin could not be found in the rendering process.
    """
    pass


class PageTypePool(object):
    """
    The central administration of plugins.
    """
    scanLock = Lock()

    def __init__(self):
        self.plugins = {}
        self._name_for_model = {}
        self._name_for_ctype_id = None
        self.detected = False
        self._file_types = None
        self._folder_types = None
        self._url_types = None

    def register(self, plugin):
        """
        Make a page type plugin known by the CMS.

        :param plugin: The plugin class, deriving from :class:`PageTypePlugin`.

        The plugin will be instantiated, just like Django does this with :class:`~django.contrib.admin.ModelAdmin` classes.
        If a plugin is already registered, this will raise a :class:`PluginAlreadyRegistered` exception.
        """
        # Duct-Typing does not suffice here, avoid hard to debug problems by upfront checks.
        assert issubclass(plugin, PageTypePlugin), "The plugin must inherit from `PageTypePlugin`"
        assert plugin.model, "The plugin has no model defined"
        assert issubclass(plugin.model, UrlNode), "The plugin model must inherit from `UrlNode` or `Page`."

        name = plugin.__name__
        if name in self.plugins:
            raise PageTypeAlreadyRegistered("[%s] a plugin with this name is already registered" % name)

        # Reset some caches
        self._folder_types = None
        self._file_types = None
        self._url_types = None

        # Make a single static instance, similar to ModelAdmin.
        plugin_instance = plugin()
        self.plugins[name] = plugin_instance
        self._name_for_model[plugin.model] = name       # Track reverse for rendering

        # Only update lazy indexes if already created
        if self._name_for_ctype_id is not None:
            self._name_for_ctype_id[plugin_instance.type_id] = name

        return plugin  # Allow class decorator syntax

    def get_plugins(self):
        """
        Return the :class:`PageTypePlugin` instances which are loaded.
        """
        self._import_plugins()
        return list(self.plugins.values())

    def get_model_classes(self):
        """
        Return all model classes which are exposed by page types.
        Each model derives from :class:`~fluent_pages.models.Page` .
        """
        self._import_plugins()
        return [plugin.model for plugin in itervalues(self.plugins)]

    def get_plugin_by_model(self, model_class):
        """
        Return the corresponding :class:`PageTypePlugin` for a given model.
        """
        self._import_plugins()                   # could happen during rendering that no plugin scan happened yet.
        assert issubclass(model_class, UrlNode)  # avoid confusion between model instance and class here!

        try:
            name = self._name_for_model[model_class]
        except KeyError:
            raise PageTypeNotFound("No plugin found for model '{0}'.".format(model_class.__name__))
        return self.plugins[name]

    def _get_plugin_by_content_type(self, contenttype):
        self._import_plugins()
        self._setup_lazy_indexes()

        ct_id = contenttype.id if isinstance(contenttype, ContentType) else int(contenttype)
        try:
            name = self._name_for_ctype_id[ct_id]
        except KeyError:
            # ContentType not found, likely a plugin is no longer registered or the app has been removed.
            try:
                # ContentType could be stale
                ct = contenttype if isinstance(contenttype, ContentType) else ContentType.objects.get_for_id(ct_id)
            except AttributeError:  # should return the stale type but Django <1.6 raises an AttributeError in fact.
                ct_name = 'stale content type'
            else:
                ct_name = '{0}.{1}'.format(ct.app_label, ct.model)
            raise PageTypeNotFound("No plugin found for content type #{0} ({1}).".format(contenttype, ct_name))

        return self.plugins[name]

    def _setup_lazy_indexes(self):
        if self._name_for_ctype_id is None:
            self._name_for_ctype_id = {}
            for name, plugin_instance in iteritems(self.plugins):
                self._name_for_ctype_id[plugin_instance.type_id] = name

    def get_file_types(self):
        """
        Return the :class:`~django.contrib.contenttypes.models.ContentType` id's
        of page types that act like files (no slash or children).
        """
        if self._file_types is None:
            ct_ids = []
            for plugin in self.get_plugins():
                if plugin.is_file:
                    ct_ids.append(plugin.type_id)
            self._file_types = ct_ids  # file_types is reset during plugin scan.

        return self._file_types

    def get_folder_types(self):
        """
        Return the :class:`~django.contrib.contenttypes.models.ContentType` id's
        of page types that operate as a container for sub pages.
        """
        if self._folder_types is None:
            ct_ids = []
            for plugin in self.get_plugins():
                if plugin.can_have_children and not plugin.is_file:
                    ct_ids.append(plugin.type_id)
            self._folder_types = ct_ids  # folder_types is reset during plugin scan.

        return self._folder_types

    def get_url_pattern_types(self):
        """
        Return the :class:`~django.contrib.contenttypes.models.ContentType` id's
        of page types that provide URL patterns.
        """
        if self._url_types is None:
            self._url_types = [plugin.type_id for plugin in self.get_url_pattern_plugins()]

        return self._url_types

    def get_url_pattern_plugins(self):
        """
        Return the :class:`PageTypePlugin` instances that provide URL patterns.
        """
        plugins = []
        for plugin in self.get_plugins():
            if plugin.urls is not None:
                plugins.append(plugin)
        return plugins

    def _import_plugins(self):
        """
        Internal function, ensure all plugin packages are imported.
        """
        if self.detected:
            return

        # In some cases, plugin scanning may start during a request.
        # Make sure there is only one thread scanning for plugins.
        self.scanLock.acquire()
        if self.detected:
            return  # previous threaded released + completed

        try:
            import_apps_submodule("page_type_plugins")
            self.detected = True
        finally:
            self.scanLock.release()


#: The global plugin pool, a instance of the :class:`PageTypePool` class.
page_type_pool = PageTypePool()
