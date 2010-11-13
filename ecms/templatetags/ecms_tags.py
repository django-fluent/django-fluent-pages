"""
Template tags to request ECMS content in the template
"""
from ecms.models import CmsObject
from django.template import Template, Library, Node, Context
from django.template.loader import get_template

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
    template_name = 'ecms/parts/breadcrumb.html'

    def get_context_data(self, context):
        page  = _ecms_get_current_page(context)  # CmsObject()
        items = page.breadcrumb # list(CmsObject)

        return {'breadcrumb': items}


class EcmsTopLevelMenuNode(SimpleInclusionNode):
    template_name = 'ecms/parts/toplevel_menu.html'

    def get_context_data(self, context):
        page  = _ecms_get_current_page(context)
        items = CmsObject.objects.toplevel_navigation(current_page=page)
        return {'menu_items': items}


class EcmsSubMenuNode(Node):
    def render(self, context):
        page = _ecms_get_current_page(context)



# ---- Util functions ----

def _ecms_get_current_page(context):
    # context = Context()
    assert context.has_key('request'), "ECMS functions require a 'request' object in the context, is RequestProcessor not used?"
    request = context['request']

    # Load on demand, e.g. calling the ecms template tags outside the standard view.
    if not request._ecms_current_page:
        request._ecms_current_page = CmsObject.objects.get_for_path(request.path)

    return request._ecms_current_page
