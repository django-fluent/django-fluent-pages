from django.contrib.admin.views.main import ChangeList
from django.template import Library, Node, TemplateSyntaxError, Variable, Context
from django.utils.safestring import mark_safe
from mptt.templatetags.mptt_tags import cache_tree_children
from fluent_pages.templatetags.stylable_admin_list import stylable_items_for_result, stylable_column_repr

register = Library()


class BreadcrumbScope(Node):
    def __init__(self, base_opts, nodelist):
        self.base_opts = base_opts
        self.nodelist = nodelist   # Note, takes advantage of Node.child_nodelists

    @classmethod
    def parse(cls, parser, token):
        bits = token.split_contents()
        if len(bits) == 2:
            (tagname, base_opts) = bits
            base_opts = parser.compile_filter(base_opts)
            nodelist = parser.parse(('endbreadcrumb_scope',))
            parser.delete_first_token()

            return cls(
                base_opts=base_opts,
                nodelist=nodelist
            )
        else:
            raise TemplateSyntaxError("{0} tag expects 1 argument".format(token.contents[0]))


    def render(self, context):
        # app_label is really hard to overwrite in the standard Django ModelAdmin.
        # To insert it in the template, the entire render_change_form() and delete_view() have to copied and adjusted.
        # Instead, overwrite them here.
        base_opts = self.base_opts.resolve(context)
        new_vars = {}
        if base_opts and not isinstance(base_opts, basestring):
            new_vars = {
                'app_label': base_opts.app_label,  # What this is all about
                'opts': base_opts,
            }

        d = context.push()
        d.update(new_vars)
        html = self.nodelist.render(context)
        context.pop()
        return html


@register.tag
def breadcrumb_scope(parser, token):
    return BreadcrumbScope.parse(parser, token)



class AdminListRecurseTreeNode(Node):
    def __init__(self, template_nodes, cl_var):
        self.template_nodes = template_nodes
        self.cl_var = cl_var

    def _render_node(self, context, cl, node):
        bits = []
        context.push()
        for child in node.get_children():
            context['columns'] = self._get_column_repr(cl, child)
            context['node'] = child
            bits.append(self._render_node(context, cl, child))

        context['columns'] = self._get_column_repr(cl, node)
        context['node'] = node
        context['children'] = mark_safe(u''.join(bits))
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def render(self, context):
        cl = self.cl_var.resolve(context)
        assert isinstance(cl, ChangeList), "cl variable should be an admin ChangeList"  # Also assists PyCharm
        roots = cache_tree_children(cl.result_list)
        bits = [self._render_node(context, cl, node) for node in roots]
        return ''.join(bits)

    def _get_column_repr(self, cl, node):
        columns = []
        for field_name in cl.list_display:
            html, row_class_ = stylable_column_repr(cl, node, field_name)
            columns.append((field_name, html))
        return columns


@register.tag
def adminlist_recursetree(parser, token):
    """
    Very similar to the mptt recursetree, except that it also returns the styled admin code.
    """
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError(_('%s tag requires an admin ChangeList') % bits[0])

    cl_var = Variable(bits[1])

    template_nodes = parser.parse(('endadminlist_recursetree',))
    parser.delete_first_token()

    return AdminListRecurseTreeNode(template_nodes, cl_var)
