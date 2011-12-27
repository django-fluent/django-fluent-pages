"""
Template tags to request ECMS content in the template
"""
from django.contrib.sites.models import Site
from django.template import TemplateSyntaxError, Library, Node, Context, defaulttags
from django.template.loader import get_template
from fluent_pages.models import CmsObject
from fluent_contents.templatetags.placeholder_tags import PagePlaceholderNode
from fluent_pages.models.navigation import CmsObjectNavigationNode

# Export the tags
register = Library()


# ---- Template node parsing ----

def _parse_token_kwargs(parser, token, allowed_fields):
    """
    Parse the template arguments in kwargs syntax.
    Returns a dictionary with FilterExpression objects.
    """
    bits = token.split_contents()
    remaining_bits = bits[1:]
    kwargs = defaulttags.token_kwargs(remaining_bits, parser)

    # Validate the allowed arguments, to make things easier for template developers
    for name in kwargs:
        if name not in allowed_fields:
            raise AttributeError("The option %s=... cannot be used in '%s'.\nPossible options are: %s." % (name, bits[0], ", ".join(allowed_fields)))
    return kwargs


def _resolve_token_kwargs(kwargs, context):
    return dict([(key, val.resolve(context)) for key, val in kwargs.iteritems()])


@register.tag(name='render_ecms_breadcrumb')
def _parse_ecms_breadcrumb(parser, token):
    return EcmsBreadcrumbNode()


@register.tag(name='render_ecms_menu')
def _parse_ecms_menu(parser, token):
    kwargs = _parse_token_kwargs(parser, token, ('max_depth',))
    return EcmsMenuNode(**kwargs)


@register.tag(name='render_ecms_region')
def _parse_ecms_region(parser, token):
    try:
        (tag_name, region_var_name) = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    # TODO: proper parsing of meta_kwargs
    return EcmsRegionNode(
        parent_expr=parser.compile_filter('ecms_page'),
        slot_expr=parser.compile_filter(region_var_name),
        meta_kwargs={},
    )


@register.tag(name='get_ecms_vars')
def _parse_get_ecms_vars(parser, token):
    return EcmsGetVarsNode()


# ---- All template nodes ----

# Please take thread-safety in mind when coding the node classes:
# Only static/unmodified values (like template tag args) should be assigned to self.


class SimpleInclusionNode(Node):
    """
    Base class to render a template tag with a template.
    """
    template_name = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_context_data(self, context, token_kwargs):
        raise NotImplementedError()

    def render(self, context):
        # Get template nodes, and cache it.
        if not getattr(self, 'nodelist', False):
            tpl = get_template(self.template_name)
            self.nodelist = tpl.nodelist

        # Resolve token kwargs
        token_kwargs = _resolve_token_kwargs(self.kwargs, context)

        # Render the node
        data = self.get_context_data(context, token_kwargs)
        new_context = Context(data, autoescape=context.autoescape)
        return self.nodelist.render(new_context)


class EcmsBreadcrumbNode(SimpleInclusionNode):
    """
    Template node for breadcrumb.
    """
    template_name = 'fluent_pages/parts/breadcrumb.html'

    def get_context_data(self, context, token_kwargs):
        page  = _get_current_page(context)  # CmsObject()
        items = page.breadcrumb # list(CmsObject)

        return {'breadcrumb': items}


class EcmsMenuNode(SimpleInclusionNode):
    """
    Template Node for topmenu
    """
    template_name = 'fluent_pages/parts/menu.html'

    def get_context_data(self, context, token_kwargs):
        # Get page
        page      = _get_current_page(context)
        top_pages = CmsObject.objects.toplevel_navigation(current_page=page)

        # Make iterable context
        menu_items = [CmsObjectNavigationNode(page, **token_kwargs) for page in top_pages]
        return {'menu_items': menu_items}


class EcmsRegionNode(PagePlaceholderNode):
    """
    Template Node for a region.
    """
    pass


class EcmsGetVarsNode(Node):
    """
    Template Node to setup an application page.

    When a template is used for an application page,
    add the following contents to make it work:

        {% load ecms_tags %}

        {% ecms_get_vars %}
    """
    def render(self, context):
        # If the current URL does not overlay a page,
        # create a dummy item to handle the standard rendering.
        current_site = None
        current_page = None

        try:
            current_page = _get_current_page(context)
            current_site = current_page.parent_site
        except CmsObject.DoesNotExist:
            # Detect current site
            request = _get_request(context)
            current_site = Site.objects.get_current(request)

            # Allow {% render_ecms_menu %} to operate.
            dummy_page = CmsObject(title='', in_navigation=False, override_url=request.path, status=CmsObject.HIDDEN, parent_site=current_site)
            request._ecms_current_page = dummy_page

        # Automatically add 'ecms_site', allows "default:ecms_site.domain" to work.
        # ...and optionally - if a page exists - include 'ecms_page' too.
        if not context.has_key('ecms_site'):
            ecms_vars = {'ecms_site': current_site}
            if current_page and not context.has_key('ecms_page'):
                ecms_vars['ecms_page'] = current_page

            context.update(ecms_vars)

        return ''



# ---- Util functions ----

def _get_current_page(context):
    """
    Fetch the current page.
    """
    request = _get_request(context)

    # This is a load-on-demand attribute, to allow calling the ecms template tags outside the standard view.
    # When the current page is not specified, do auto-detection.
    if not hasattr(request, '_ecms_current_page'):
        try:
            # First start with something you can control,
            # and likely want to mimic from the standard view.
            request._ecms_current_page = context['ecms_page']
        except KeyError:
            try:
                # Then try looking up environmental properties.
                request._ecms_current_page = CmsObject.objects.get_for_path(request.path)
            except CmsObject.DoesNotExist, e:
                # Be descriptive. This saves precious developer time.
                raise CmsObject.DoesNotExist("Could not detect current page.\n"
                                             "- " + unicode(e) + "\n"
                                             "- No context variable named 'ecms_page' found.")

    return request._ecms_current_page  # is a CmsObject


def _get_request(context):
    """
    Fetch the request from the context.

    This enforces the use of a RequestProcessor, e.g.

        render_to_response("page.html", context, context_instance=RequestContext(request))
    """
    assert context.has_key('request'), "ECMS functions require a 'request' object in the context, is RequestContext not used?"
    return context['request']

