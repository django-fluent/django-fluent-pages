"""
Template tags to request fluent page content in the template.
Load this module using:

.. code-block:: html+django

    {% load fluent_pages_tags %}
"""
from future.builtins import str
from six import integer_types, string_types
from six import iteritems
from django.contrib.sites.models import Site
from django.utils.functional import SimpleLazyObject
from django.template import Library, TemplateSyntaxError
from tag_parser import template_tag
from tag_parser.basetags import BaseInclusionNode, BaseNode

from fluent_pages.models import UrlNode
from fluent_pages.models.navigation import PageNavigationNode
from fluent_pages.models.utils import prefill_parent_site


register = Library()


# Please take thread-safety in mind when coding the node classes:
# Only static/unmodified values (like template tag args) should be assigned to self.


@template_tag(register, 'render_breadcrumb')
class BreadcrumbNode(BaseInclusionNode):
    """
    Render the breadcrumb of the site.

    .. code-block:: html+django

        {% render_breadcrumb template="fluent_pages/parts/breadcrumb.html" %}
    """
    tag_name = 'render_breadcrumb'
    template_name = 'fluent_pages/parts/breadcrumb.html'

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        request = _get_request(parent_context)
        try:
            page  = _get_current_page(parent_context)  # UrlNode
        except UrlNode.DoesNotExist:
            # Typically happens when {% render_breadcrumb %} is used on 404 pages,
            # there is no breadcrumb possible there.
            # NOTE: if desired, we could add an option to use UrlNode.objects.best_match_for_path() here.
            items = []
            page = None
            site = None
        else:
            items = page.breadcrumb # list(UrlNode)
            site = SimpleLazyObject(lambda: page.parent_site),  # Only read if really used, then cache.

        return {
            'parent': parent_context,
            'request': request,
            'breadcrumb': items,
            'page': page,
            'site': site,
        }


def get_node_kwargs(tag_kwargs):
    """
    Return a dict suitable for passing as kwargs to a PageNavigationNode object
    """
    return dict(
        (k, v)
        for k, v in iteritems(tag_kwargs)
        if k in ('max_depth',)
    )


@template_tag(register, 'render_menu')
class MenuNode(BaseInclusionNode):
    """
    Render the menu of the site.

    .. code-block:: html+django

        {% render_menu max_depth=1 template="fluent_pages/parts/menu.html" %}
        {% render_menu parent="/page/url/" max_depth=1 template="fluent_pages/parts/menu.html" %}
    """
    template_name = 'fluent_pages/parts/menu.html'
    allowed_kwargs = ('max_depth', 'template', 'parent')

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        # Get page objects
        request = _get_request(parent_context)
        user = request.user
        try:
            current_page = _get_current_page(parent_context)
        except UrlNode.DoesNotExist:
            current_page = None

        if 'parent' in tag_kwargs:
            # if we've been provided a parent kwarg then we want to filter
            parent_value = tag_kwargs['parent']

            if isinstance(parent_value, string_types):
                # if we've been provided a string then we lookup based on the path/url
                try:
                    parent = UrlNode.objects.get_for_path(parent_value)
                except UrlNode.DoesNotExist:
                    return {'menu_items': []}
                top_pages = parent.children.in_navigation(for_user=user)  # Can't do parent___cached_key due to polymorphic queryset code.
            elif isinstance(parent_value, integer_types):
                # If we've been provided an int then we lookup based on the id of the page
                top_pages = UrlNode.objects.in_navigation(for_user=user).filter(parent_id=parent_value)
            elif isinstance(parent_value, UrlNode):
                # If we've been given a Page or UrlNode then there's no lookup necessary
                top_pages = parent_value.children.in_navigation(for_user=user)
            else:
                raise TemplateSyntaxError("The 'render_menu' tag only allows an URL path, page id or page object for the 'parent' keyword")
        else:
            # otherwise get the top level nav for the current page
            top_pages = UrlNode.objects.toplevel_navigation(current_page=current_page, for_user=user)

        # Construct a PageNavigationNode for every page, that allows simple iteration of the tree.
        node_kwargs = get_node_kwargs(tag_kwargs)
        return {
            'parent': parent_context,
            'request': request,
            'menu_items': [
                PageNavigationNode(page, current_page=current_page, for_user=user, **node_kwargs) for page in top_pages
            ]
        }


@template_tag(register, 'get_fluent_page_vars')
class GetVarsNode(BaseNode):
    """
    Template Node to setup an application page.

    Introduces the ``site`` and ``page`` variables in the template.
    This can be used for pages that are rendered by a separate application.

    .. code-block:: html+django

        {% get_fluent_page_vars %}
    """

    def render_tag(self, context, *args, **kwargs):
        # If the current URL does not overlay a page,
        # create a dummy item to handle the standard rendering.
        try:
            current_page = _get_current_page(context)
            current_site = current_page.parent_site
        except UrlNode.DoesNotExist:
            # Detect current site
            request = _get_request(context)
            current_page = None
            current_site = Site.objects.get_current()

            # Allow {% render_menu %} to operate.
            dummy_page = UrlNode(title='', in_navigation=False, override_url=request.path, status=UrlNode.DRAFT, parent_site=current_site)
            request._current_fluent_page = dummy_page

        # Automatically add 'site', allows "default:site.domain" to work.
        # ...and optionally - if a page exists - include 'page' too.
        extra_context = {}
        if 'site' not in context:
            extra_context['site'] = current_site
        if current_page and 'page' not in context:
            extra_context['page'] = current_page

        if extra_context:
            context.update(extra_context)

        return ''


# ---- Util functions ----

def _get_current_page(context):
    """
    Fetch the current page.
    """
    request = _get_request(context)

    # This is a load-on-demand attribute, to allow calling the template tags outside the standard view.
    # When the current page is not specified, do auto-detection.
    if not hasattr(request, '_current_fluent_page'):
        try:
            # First start with something you can control,
            # and likely want to mimic from the standard view.
            current_page = context['page']
        except KeyError:
            try:
                # Then try looking up environmental properties.
                current_page = UrlNode.objects.get_for_path(request.path)
            except UrlNode.DoesNotExist as e:
                # Be descriptive. This saves precious developer time.
                raise UrlNode.DoesNotExist("Could not detect current page.\n"
                                           "- " + str(e) + "\n"
                                           "- No context variable named 'page' found.")

        if not isinstance(current_page, UrlNode):
            raise UrlNode.DoesNotExist("The 'page' context variable is not a valid page")

        prefill_parent_site(current_page)
        request._current_fluent_page = current_page

    return request._current_fluent_page  # is a UrlNode


def _get_request(context):
    """
    Fetch the request from the context.
    This enforces the use of the template :class:`~django.template.RequestContext`,
    and provides meaningful errors if this is omitted.
    """
    assert 'request' in context, "The fluent_pages_tags library requires a 'request' object in the context! Is RequestContext not used, or 'django.core.context_processors.request' not included in TEMPLATE_CONTEXT_PROCESSORS?"
    return context['request']


if False and __debug__:
    # This only exists to make PyCharm happy:
    # The real syntax should be passing the ``.parse`` method to the function.
    register.tag('render_breadcrumb', BreadcrumbNode)
    register.tag('render_menu', MenuNode)
    register.tag('get_fluent_page_vars', GetVarsNode)
