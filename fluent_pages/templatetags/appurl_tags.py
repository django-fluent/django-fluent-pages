"""
Template tag to resolve page URLs which have an URLconf attached to them.
Load this module using:

.. code-block:: html+django

    {% load appurl_tags %}

Usage:

.. code-block:: html+django

    {% appurl "my_viewname" %}

    {% appurl "my_viewname" arg1 arg2 %}

    {% appurl "my_viewname" kwarg1=value kwargs2=value %}

"""
from django.template import Library
from django.utils.encoding import smart_str
from fluent_pages.models.db import UrlNode
from fluent_pages.urlresolvers import mixed_reverse
from tag_parser.basetags import BaseNode

register = Library()

__all__ = (
    'AppUrlNode', 'appurl',
)


class AppUrlNode(BaseNode):
    min_args = 1
    max_args = None

    def render_tag(self, context, *tag_args, **tag_kwargs):
        view_name = tag_args[0]
        url_args = tag_args[1::]
        url_kwargs = dict([(smart_str(name, 'ascii'), value) for name, value in tag_kwargs.items()])

        # If the page is a UrlNode, use it as base for the pages.
        page = context.get('page')
        if not isinstance(page, UrlNode):
            page = None

        # Try a normal URLConf URL, then an app URL
        return mixed_reverse(view_name, args=url_args, kwargs=url_kwargs, current_app=context.current_app, current_page=page)


@register.tag
def appurl(parser, token):
    # This tag parser function kept because it's also used as export.
    # In docs/newpagetypes/urls.rst, it's also described.
    return AppUrlNode.parse(parser, token)
