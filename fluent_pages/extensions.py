"""
Special classes to extend the module; e.g. page type plugins.

The extension mechanism is provided for projects that benefit
from a tighter integration then the Django URLconf can provide.

The API uses a registration system.
While plugins can be easily detected via ``__subclasses__()``, the register approach is less magic and more explicit.
Having to do an explicit register ensures future compatibility with other API's like reversion.
"""
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import RegexURLResolver
from django.db import DatabaseError
from django.template.response import TemplateResponse
from django.utils.functional import SimpleLazyObject
from django.utils.importlib import import_module
from fluent_pages.admin import PageAdmin
from fluent_pages.models import UrlNode
from threading import Lock

__all__ = (
    'PageTypePlugin', 'PageTypeAlreadyRegistered', 'PageTypeNotFound', 'PageTypePool', 'page_type_pool'
)



class PageTypePlugin(object):
    """
    The base class for a page type plugin.

    To create a new plugin, derive from this class and call :func:`plugin_pool.register <PluginPool.register>` to enable it.
    """
    __metaclass__ = forms.MediaDefiningClass

    # -- Settings to override:

    #: The model to use, must derive from :class:`fluent_contents.models.UrlNode`.
    model = None

    #: The modeladmin instance to customize the screen.
    model_admin = PageAdmin

    #: The template to render the frontend HTML output.
    render_template = None

    #: The class to use by default for the response
    response_class = TemplateResponse

    #: Whether the page type represents a file (no slash or children)
    is_file = False

    #: Whether the page type allows to have children (unless `is_file`` is true)
    can_have_children = True

    #: Set the URLs which the page serves provides the current node. Can either be a URLconf module, or inline pattern list.
    urls = None

    #: The sorting priority for the add page.
    sort_priority = 100


    def __init__(self):
        self._type_id = None
        self._url_resolver = None


    def __repr__(self):
        return '<{0} for {1} model>'.format(self.__class__.__name__, unicode(self.model.__name__).encode('ascii'))


    @property
    def verbose_name(self):
        """
        The title for the plugin, by default it reads the ``verbose_name`` of the model.
        """
        return self.model._meta.verbose_name


    @property
    def type_name(self):
        """
        Return the classname of the model, this is mainly provided for templates.
        """
        return self.model.__name__


    @property
    def type_id(self):
        """
        Shortcut to retrieving the ContentType id of the model.
        """
        if self._type_id is None:
            try:
                self._type_id = ContentType.objects.get_for_model(self.model).id
            except DatabaseError as e:
                raise DatabaseError("Unable to fetch ContentType object, is a plugin being registered before the initial syncdb? (original error: {0})".format(str(e)))
        return self._type_id


    def get_model_instances(self):
        """
        Return the model instances the plugin has created.
        """
        return self.model.objects.all()


    def get_response(self, request, page, **kwargs):
        """
        Return the Django response for the page.
        """
        render_template = self.get_render_template(request, page, **kwargs)
        if not render_template:
            raise ImproperlyConfigured("{0} should either provide a definition of 'render_template' or an implementation of 'get_response()'".format(self.__class__.__name__))

        context = self.get_context(request, page, **kwargs)
        return self.response_class(
            request = request,
            template = render_template,
            context = context,
        )


    def get_render_template(self, request, page, **kwargs):
        """
        Return the template to render for the specific `page` or `request`,
        By default it uses the ``render_template`` attribute.
        """
        return self.render_template


    def get_context(self, request, page, **kwargs):
        """
        Return the context to use in the template defined by ``render_template`` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """
        return {
            'page': page,
            'site': SimpleLazyObject(lambda: page.parent_site),  # delay query until read
        }


    def get_url_resolver(self):
        """
        Return the URL patterns of the page type.
        """
        if self._url_resolver is None:
            if self.urls is None:
                return None
            elif isinstance(self.urls, basestring):
                mod = import_module(self.urls)
                if not hasattr(mod, 'urlpatterns'):
                    raise ImproperlyConfigured("URLConf `{0}` has no urlpatterns attribute".format(self.urls))
                patterns = getattr(mod, 'urlpatterns')
            elif isinstance(self.urls, (list, tuple)):
                patterns = self.urls
            else:
                raise ImproperlyConfigured("Invalid value for '{0}.urls', must be string, list or tuple.".format(self.__class__.__name__))

            self._url_resolver = RegexURLResolver(r'^/', patterns)
        return self._url_resolver



# -------- Some utils --------

def _import_apps_submodule(submodule):
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


# -------- API to access plugins --------

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
        self.plugin_for_model = {}
        self.plugin_for_ctype_id = {}
        self.detected = False
        self.admin_site = admin.AdminSite()
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
        self.plugin_for_model[plugin.model] = name       # Track reverse for rendering
        self.plugin_for_ctype_id[plugin_instance.type_id] = name

        # Instantiate model admin
        self.admin_site.register(plugin.model, plugin.model_admin)
        return plugin  # Allow class decorator syntax


    def get_plugins(self):
        """
        Return the list of all plugin instances which are loaded.
        """
        self._import_plugins()
        return self.plugins.values()


    def get_model_classes(self):
        """
        Return all :class:`~fluent_contents.models.ContentItem` model classes which are exposed by plugins.
        """
        self._import_plugins()
        return [plugin.model for plugin in self.plugins.values()]


    def get_plugin_by_model(self, model_class):
        """
        Return the corresponding plugin for a given model.
        """
        self._import_plugins()                   # could happen during rendering that no plugin scan happened yet.
        assert issubclass(model_class, UrlNode)  # avoid confusion between model instance and class here!

        try:
            name = self.plugin_for_model[model_class]
        except KeyError:
            raise PageTypeNotFound("No plugin found for model '{0}'.".format(model_class.__name__))
        return self.plugins[name]


    def _get_plugin_by_content_type(self, contenttype):
        self._import_plugins()

        ct_id = contenttype.id if isinstance(contenttype, ContentType) else int(contenttype)
        try:
            name = self.plugin_for_ctype_id[ct_id]
        except KeyError:
            raise PageTypeNotFound("No plugin found for content type '{0}'.".format(contenttype))
        return self.plugins[name]


    def get_model_admin(self, model_class):
        """
        Access the model admin object instantiated for the plugin.
        """
        self._import_plugins()                   # could happen during rendering that no plugin scan happened yet.
        assert issubclass(model_class, UrlNode)  # avoid confusion between model instance and class here!

        try:
            return self.admin_site._registry[model_class]
        except KeyError:
            raise PageTypeNotFound("No ModelAdmin found for model '{0}'.".format(model_class.__name__))


    def get_file_types(self):
        """
        Return the page content types which act like files (no slash or children).
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
        Return the page content types which operate as a container for sub pages.
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
        Return the page content types which can provide URL patterns.
        """
        if self._url_types is None:
            self._url_types = [plugin.type_id for plugin in self.get_url_pattern_plugins()]

        return self._url_types


    def get_url_pattern_plugins(self):
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
            _import_apps_submodule("page_type_plugins")
            self.detected = True
        finally:
            self.scanLock.release()


#: The global plugin pool, a instance of the :class:`PluginPool` class.
page_type_pool = PageTypePool()
