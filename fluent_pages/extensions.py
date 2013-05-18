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
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import RegexURLResolver
from django.db import DatabaseError
from django.template.response import TemplateResponse
from django.utils.functional import SimpleLazyObject
from django.utils.importlib import import_module
from fluent_pages import appsettings
from fluent_pages.admin import PageAdmin
from fluent_pages.models import UrlNode
from threading import Lock

__all__ = (
    'PageTypePlugin', 'PageTypeAlreadyRegistered', 'PageTypeNotFound', 'PageTypePool', 'page_type_pool'
)



class PageTypePlugin(object):
    """
    The base class for a page type plugin.

    To create a new plugin, derive from this class and call :func:`page_type_pool.register <PageTypePool.register>` to enable it.
    For example:

    .. code-block:: python

        from fluent_pages.extensions import PageTypePlugin, page_type_pool
        from mycms.models import MyCustomPage

        @page_type_pool.register
        class MyCustomPagePlugin(PageTypePlugin):
            model = MyCustomPage
            render_template = "mycustompage/example.html"

    As minimal configuration, specify the :attr:`model` and :attr:`render_template` fields.
    The :attr:`model` should be a subclass of the :class:`~fluent_pages.models.Page` model class.

    .. note::
        When the plugin is registered in the :attr:`page_type_pool`, it will be instantiated only once.
        It is therefore not possible to store per-request state at the page type object.
        This is similar to the behavior of the :class:`~django.contrib.admin.ModelAdmin` classes in Django.

    To customize the admin, define the :attr:`model_admin` attribute.
    The provided class should inherit from the :class:`~fluent_pages.admin.PageAdmin` class.

    The output of a page is fully customizable in the page type plugin.
    By default, :attr:`render_template` will be used but you can also override
    :func:`get_render_template`, :func:`get_context` or even :func:`get_response`.
    The latter gives full control over the :class:`~django.http.HttpResponse` to send to the client.

    Page types can provide additional views, relative to the location where the page is placed in the tree.
    A shopping module for example, can display products as sub pages.
    Provide an URLconf to the :attr:`urls` attribute to use this feature,
    and resolve those URLs using the :mod:`fluent_pages.urlresolvers` module.
    """
    __metaclass__ = forms.MediaDefiningClass

    # -- Settings to override:

    #: Defines the model to use to store the custom fields.
    #: It must derive from :class:`~fluent_pages.models.Page`.
    model = None

    #: Defines the :class:`~django.contrib.admin.ModelAdmin` class to customize the screen.
    #: It should inherit from :class:`~fluent_pages.admin.PageAdmin`.
    model_admin = PageAdmin

    #: Defines the template to use for rendering the page.
    render_template = None

    #: Defines the default class to use for the response.
    response_class = TemplateResponse

    #: Defines the page type represents a file; it neither has appended slash or does it allow children.
    is_file = False

    #: Defines whether users are allowed to place sub pages below this node. When :attr:`is_file` is ``True``, this is never possible.
    can_have_children = True

    #: Defines the URLs that the page provides relative to the current node.
    #: This can either be the name of a Python module with ``urlpatterns`` in it,
    #: or a direct inline :func:`~django.conf.urls.patterns` list.
    urls = None

    #: The sorting priority for the page type in the "Add Page" dialog of the admin.
    sort_priority = 100


    def __init__(self):
        self._type_id = None
        self._url_resolver = None


    def __repr__(self):
        return '<{0} for {1} model>'.format(self.__class__.__name__, unicode(self.model.__name__).encode('ascii'))


    @property
    def verbose_name(self):
        """
        Returns the title for the plugin, by default it reads the ``verbose_name`` of the model.
        """
        return self.model._meta.verbose_name


    @property
    def type_name(self):
        """
        Return the class name of the model, this is mainly provided for templates.
        """
        return self.model.__name__


    @property
    def type_id(self):
        """
        Returns the :class:`~django.contrib.contenttypes.models.ContentType` id of the model.
        """
        if self._type_id is None:
            try:
                self._type_id = ContentType.objects.get_for_model(self.model).id
            except DatabaseError as e:
                raise DatabaseError("Unable to fetch ContentType object, is a plugin being registered before the initial syncdb? (original error: {0})".format(str(e)))
        return self._type_id


    def get_model_instances(self):
        """
        Return all :class:`~fluent_pages.models.Page` instances that are has created using this page types.
        """
        return self.model.objects.all()


    def get_response(self, request, page, **kwargs):
        """
        Render the page, and return the Django :class:`~django.http.HttpResponse`.

        This is the main function to generate output of the page.
        By default, it uses :func:`get_render_template`, :func:`get_context` and :attr:`response_class`
        to generate the output of the page. The behavior can be replaced completely by overriding this function.
        """
        render_template = self.get_render_template(request, page, **kwargs)
        if not render_template:
            raise ImproperlyConfigured("{0} should either provide a definition of `render_template`, `urls` or an implementation of `get_response()`".format(self.__class__.__name__))

        context = self.get_context(request, page, **kwargs)
        return self.response_class(
            request = request,
            template = render_template,
            context = context,
        )


    def get_render_template(self, request, page, **kwargs):
        """
        Return the template to render for the specific `page` or `request`,
        By default it uses the :attr:`render_template` attribute.
        """
        return self.render_template


    def get_context(self, request, page, **kwargs):
        """
        Return the context to use in the template defined by :attr:`render_template` (or :func:`get_render_template`).
        By default, it returns the model instance as ``instance`` field in the template.
        """
        return {
            'FLUENT_PAGES_BASE_TEMPLATE': appsettings.FLUENT_PAGES_BASE_TEMPLATE,
            'page': page,
            'site': SimpleLazyObject(lambda: page.parent_site),  # delay query until read
        }


    def get_url_resolver(self):
        """
        Access the URL resolver of the page type.
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

        return plugin  # Allow class decorator syntax


    def get_plugins(self):
        """
        Return the :class:`PageTypePlugin` instances which are loaded.
        """
        self._import_plugins()
        return self.plugins.values()


    def get_model_classes(self):
        """
        Return all model classes which are exposed by page types.
        Each model derives from :class:`~fluent_pages.models.Page` .
        """
        self._import_plugins()
        return [plugin.model for plugin in self.plugins.values()]


    def get_plugin_by_model(self, model_class):
        """
        Return the corresponding :class:`PageTypePlugin` for a given model.
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
            _import_apps_submodule("page_type_plugins")
            self.detected = True
        finally:
            self.scanLock.release()


#: The global plugin pool, a instance of the :class:`PageTypePool` class.
page_type_pool = PageTypePool()
