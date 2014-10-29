"""
The base classes to create a page which can display *django-fluent-contents* models.

The API to interface with *django-fluent-contents* is public, and documented for this reason.
In fact, this module is just a tiny bridge between the page type plugins and the *django-fluent-pages* API.
It can be used to create custom page types that display :class:`~fluent_contents.models.ContentItem` objects.

The following parts are provided:

* The admin class; :class:`FluentContentsPageAdmin`
* The page type model: :class:`FluentContentsPage`
* The plugin class: :class:`FluentContentsPagePlugin`
"""
from .models import FluentContentsPage
from .admin import FluentContentsPageAdmin
from .page_type_plugins import FluentContentsPagePlugin

__all__ = (
    'FluentContentsPageAdmin',
    'FluentContentsPage',
    'FluentContentsPagePlugin',
)
