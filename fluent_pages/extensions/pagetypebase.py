"""
Internal module for the plugin system,
the API is exposed via __init__.py
"""
from future.builtins import str
from future.utils import with_metaclass

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import RegexURLResolver
from django.db import DatabaseError
from django.template.response import TemplateResponse
from django.utils.functional import SimpleLazyObject

from fluent_pages import appsettings
from fluent_pages.adminui import PageAdmin

from six import string_types

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module  # Python 2.6


__all__ = (
    'PageTypePlugin',
)


class PageTypePlugin(with_metaclass(forms.MediaDefiningClass, object)):
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

    #: .. versionadded:: 0.9
    #: Tell whether the page type should be displayed in the sitemaps by default.
    #: This value can be changed for most pages in the admin interface.
    default_in_sitemaps = True

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
        return '<{0} for {1} model>'.format(self.__class__.__name__, str(self.model.__name__).encode('ascii'))

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

        Note that this function can also be called by custom views
        when those views implement the :class:`~fluent_pages.views.CurrentPageMixin`
        or :class:`~fluent_pages.views.CurrentPageTemplateMixin`
        """
        return {
            'FLUENT_PAGES_BASE_TEMPLATE': appsettings.FLUENT_PAGES_BASE_TEMPLATE,
            'page': page,
            'site': SimpleLazyObject(lambda: page.parent_site),  # delay query until read
        }

    def get_view_response(self, request, page, view_func, view_args, view_kwargs):
        """
        Render the custom view that was exposed by the extra plugin URL patterns.
        This gives the ability to add extra middleware logic.
        """
        return view_func(request, *view_args, **view_kwargs)

    def get_url_resolver(self):
        """
        Access the URL resolver of the page type.
        """
        if self._url_resolver is None:
            if self.urls is None:
                return None
            elif isinstance(self.urls, string_types):
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
