from django.template import Library, Node, TemplateSyntaxError
from django.utils.encoding import smart_str
from fluent_pages.models.db import UrlNode
from fluent_pages.urlresolvers import mixed_reverse
from fluent_pages.utils.tagparsing import parse_token_kwargs

register = Library()


class AppUrlNode(Node):
    def __init__(self, name_expr, args, kwargs):
        self.name_expr = name_expr
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def parse(cls, parser, token):
        bits = token.split_contents()
        args, kwargs = parse_token_kwargs(parser, bits, True, True)
        if len(args) < 1:
            raise TemplateSyntaxError("'{0}' tag expects one argument!".format(bits[0]))
        return cls(args[0], args[1::], kwargs)

    def render(self, context):
        # If the page is a UrlNode, use it as base for the pages.
        page = context['page']
        if not isinstance(page, UrlNode):
            page = None

        view_name = self.name_expr.resolve(context)
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context)) for k, v in self.kwargs.items()])

        # Try a normal URLConf URL, then an app URL
        return mixed_reverse(view_name, args=args, kwargs=kwargs, current_app=context.current_app, current_page=page)


@register.tag
def appurl(parser, token):
    return AppUrlNode.parse(parser, token)
