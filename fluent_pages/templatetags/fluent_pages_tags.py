"""
Template tags to request fluent page content in the template.

Thet tags can be loaded using:

.. code-block:: html+django

    {% load fluent_pages_tags %}
"""
from django.contrib.sites.models import Site
from django.template import Library, Node
from fluent_pages.models import UrlNode
from fluent_pages.models.navigation import PageNavigationNode
from fluent_pages.utils.basetags import ExtensibleInclusionNode

register = Library()



# Please take thread-safety in mind when coding the node classes:
# Only static/unmodified values (like template tag args) should be assigned to self.


class BreadcrumbNode(ExtensibleInclusionNode):
    """
    Template node for breadcrumb.
    """
    template_name = 'fluent_pages/parts/breadcrumb.html'

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        page  = _get_current_page(parent_context)  # CmsObject()
        items = page.breadcrumb # list(CmsObject)

        return {'breadcrumb': items}


@register.tag
def render_breadcrumb(parser, token):
    """
    Render the breadcrumb of the site.

    .. code-block:: html+django

        {% render_breadcrumb %}
        {% render_breadcrumb template="sitetheme/parts/breadcrumb.html" %}
    """
    return BreadcrumbNode.parse(parser, token)



class MenuNode(ExtensibleInclusionNode):
    """
    Template Node for topmenu
    """
    template_name = 'fluent_pages/parts/menu.html'
    allowed_kwargs = ('max_depth', 'template',)

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        # Get page
        page      = _get_current_page(parent_context)
        top_pages = UrlNode.objects.toplevel_navigation(current_page=page)

        # Make iterable context, pass subset of arguments to PageNavigationNode constructor
        node_kwargs = dict((k,v) for k, v in tag_kwargs.iteritems() if k in ('max_depth',))
        menu_items = [PageNavigationNode(page, **node_kwargs) for page in top_pages]
        return {'menu_items': menu_items}


@register.tag
def render_menu(parser, token):
    """
    Render the breadcrumb of the site.

    .. code-block:: html+django

        {% render_menu max_depth=1 template="sitetheme/parts/menu.html" %}
    """
    return MenuNode.parse(parser, token)



class GetVarsNode(Node):
    """
    Template Node to setup an application page.
    """
    def render(self, context):
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

        # Automatically add 'ecms_site', allows "default:ecms_site.domain" to work.
        # ...and optionally - if a page exists - include 'ecms_page' too.
        if not context.has_key('site'):
            extra_context = {'site': current_site}
            if current_page and not context.has_key('page'):
                extra_context['page'] = current_page

            context.update(extra_context)

        return ''


@register.tag
def get_fluent_page_vars(parser, token):
    """
    When a template is used for an application page,
    add the following contents to make it work:

    .. code-block:: html+django

        {% load fluent_pages_tags %}
        {% get_fluent_page_vars %}
    """
    return GetVarsNode()



# ---- Util functions ----

def _get_current_page(context):
    """
    Fetch the current page.
    """
    request = _get_request(context)

    # This is a load-on-demand attribute, to allow calling the ecms template tags outside the standard view.
    # When the current page is not specified, do auto-detection.
    if not hasattr(request, '_current_fluent_page'):
        try:
            # First start with something you can control,
            # and likely want to mimic from the standard view.
            request._current_fluent_page = context['page']
        except KeyError:
            try:
                # Then try looking up environmental properties.
                request._current_fluent_page = UrlNode.objects.get_for_path(request.path)
            except UrlNode.DoesNotExist, e:
                # Be descriptive. This saves precious developer time.
                raise UrlNode.DoesNotExist("Could not detect current page.\n"
                                           "- " + unicode(e) + "\n"
                                           "- No context variable named 'page' found.")

    return request._current_fluent_page  # is a CmsObject


def _get_request(context):
    """
    Fetch the request from the context.
    This enforces the use of a RequestProcessor, e.g.

    .. code-block:: python

        render_to_response("page.html", context, context_instance=RequestContext(request))
    """
    assert context.has_key('request'), "The fluent_pages_tags library requires a 'request' object in the context, is RequestContext not used?"
    return context['request']

