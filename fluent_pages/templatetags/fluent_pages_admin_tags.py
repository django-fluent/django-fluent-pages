from django.template import Library, Node, TemplateSyntaxError, Context

register = Library()


class BreadcrumbScope(Node):
    def __init__(self, base_opts, nodelist):
        self.base_opts = base_opts
        self.nodelist = nodelist

    def render(self, context):
        # app_label is really hard to overwrite in the standard Django ModelAdmin.
        # To insert it in the template, the entire render_change_form() and delete_view() have to copied and adjusted.
        # Instead, overwrite them here.
        base_opts = self.base_opts.resolve(context)
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
    try:
        (tagname, base_opts) = token.split_contents()
    except IndexError:
        raise TemplateSyntaxError("{0} tag expects 1 argument".format(token.contents[0]))

    base_opts = parser.compile_filter(base_opts)
    nodelist = parser.parse(('endbreadcrumb_scope',))
    parser.delete_first_token()

    return BreadcrumbScope(base_opts, nodelist)
