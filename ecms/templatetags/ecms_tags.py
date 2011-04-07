"""
Template tags to request ECMS content in the template
"""
from ecms.models import CmsObject, CmsSite
from django.template import Template, TemplateSyntaxError, Library, Node, Context, Variable
from django.template.loader import get_template
from ecms.navigation import CmsObjectNavigationNode

# Export the tags
register = Library()


# ---- Template node parsing ----


@register.tag(name='render_ecms_breadcrumb')
def _parse_ecms_breadcrumb(parser, token):
    return EcmsBreadcrumbNode()


@register.tag(name='render_ecms_menu')
def _parse_ecms_menu(parser, token):
    return EcmsTopLevelMenuNode()


@register.tag(name='render_ecms_sub_menu')
def _parse_ecms_sub_menu(parser, token):
    return EcmsSubMenuNode()


@register.tag(name='render_ecms_region')
def _parse_ecms_region(parser, token):
    try:
        (tag_name, region_var_name) = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return EcmsRegionNode(region_var_name)


@register.tag(name='get_ecms_vars')
def _parse_get_ecms_vars(parser, token):
    return EcmsGetVarsNode()


# ---- All template nodes ----

# Please take thread-safety in mind when coding the node classes:
# Only static/unmodified values (like template tag args) should be assigned to self.


class SimpleInclusionNode(Node):
    template_name = None

    def get_context_data(self, context):
        raise NotImplementedError()

    def render(self, context):
        # Get template nodes, and cache it.
        if not getattr(self, 'nodelist', False):
            tpl = get_template(self.template_name)
            self.nodelist = tpl.nodelist

        # Render the node
        data = self.get_context_data(context)
        new_context = Context(data, autoescape=context.autoescape)
        return self.nodelist.render(new_context)


class EcmsBreadcrumbNode(SimpleInclusionNode):
    """
    Template node for breadcrumb.
    """
    template_name = 'ecms/parts/breadcrumb.html'

    def get_context_data(self, context):
        page  = _ecms_get_current_page(context)  # CmsObject()
        items = page.breadcrumb # list(CmsObject)

        return {'breadcrumb': items}


class EcmsTopLevelMenuNode(SimpleInclusionNode):
    """
    Template Node for topmenu
    """
    template_name = 'ecms/parts/toplevel_menu.html'

    def get_context_data(self, context):
        # Get page
        page      = _ecms_get_current_page(context)
        top_pages = CmsObject.objects.toplevel_navigation(current_page=page)

        # Make iterable context
        menu_items = [CmsObjectNavigationNode(page) for page in top_pages]
        return {'menu_items': menu_items}


class EcmsSubMenuNode(Node):
    """
    Template Node for submenu.
    """
    def render(self, context):
        page = _ecms_get_current_page(context)


class EcmsRegionNode(Node):
    """
    Template Node for a region.
    """
    def __init__(self, region_var_name):
        self.region_name = region_var_name

    def render(self, context):
        page  = _ecms_get_current_page(context)
        region_name = Variable(self.region_name).resolve(context)
        items = page.regions[region_name]
        if not items:
            return "<!-- no items in region '%s' -->" % region_name
        else:
            return items.render()   # is CmsPageItemList.render()


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
            current_page = _ecms_get_current_page(context)
            current_site = current_page.parent_site
        except CmsObject.DoesNotExist:
            # Detect current site
            request = _ecms_get_request(context)
            current_site = CmsSite.objects.get_current(request)

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

def _ecms_get_current_page(context):
    """
    Fetch the current page.
    """
    request = _ecms_get_request(context)

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


def _ecms_get_request(context):
    """
    Fetch the request from the context.

    This enforces the use of a RequestProcessor, e.g.

        render_to_response("page.html", context, context_instance=RequestProcessor(request))
    """
    assert context.has_key('request'), "ECMS functions require a 'request' object in the context, is RequestProcessor not used?"
    return context['request']

