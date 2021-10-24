"""
Template tag to resolve page URLs which have an URLconf attached to them.
Load this module using:

.. code-block:: html+django

    {% load appurl_tags %}

Usage:

.. code-block:: html+django

    {% appurl "my_viewname" %}

    {% appurl "my_viewname" arg1 arg2 %}

    {% appurl "my_viewname" kwarg1=value kwargs2=value as varname %}

"""
from django.template import Library
from django.utils.encoding import smart_str
from tag_parser.basetags import BaseAssignmentOrOutputNode

from fluent_pages.models.db import UrlNode
from fluent_pages.urlresolvers import mixed_reverse

register = Library()

__all__ = ("AppUrlNode", "appurl")


class AppUrlNode(BaseAssignmentOrOutputNode):
    min_args = 1
    max_args = None
    allowed_kwargs = None  # Allow kwargs!

    def get_value(self, context, *tag_args, **tag_kwargs):
        view_name = tag_args[0]
        url_args = tag_args[1::]
        url_kwargs = {smart_str(name, "ascii"): value for name, value in tag_kwargs.items()}

        # The app_reverse() tag can handle multiple results fine if it knows what the current page is.
        # Try to find it.
        request = context.get("request")
        page = getattr(request, "_current_fluent_page", None)
        if not page:
            # There might be a 'page' variable, that was retrieved via `{% get_fluent_page_vars %}`.
            # However, django-haystack also uses this variable name, so check whether it's the correct object.
            page = context.get("page")
            if not isinstance(page, UrlNode):
                page = None

        # request.current_app is passed everywhere if available, otherwise it does not exist.
        # Somehow it needs to be assigned explicitly in the app
        # via: request.current_app = request.resolver_match.namespace
        current_app = getattr(request, "current_app", None)

        # Try a normal URLConf URL, then an app URL
        return mixed_reverse(
            view_name,
            args=url_args,
            kwargs=url_kwargs,
            current_app=current_app,
            current_page=page,
        )


@register.tag
def appurl(parser, token):
    # This tag parser function kept because it's also used as export.
    # In docs/newpagetypes/urls.rst, it's also described.
    return AppUrlNode.parse(parser, token)
