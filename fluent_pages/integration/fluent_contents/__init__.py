"""
The base classes to create a page which can display *django-fluent-contents* models.

The API to interface with *django-fluent-contents* is public, and documented for this reason.
In fact, this module is just a tiny bridge between the page type plugins and the *django-fluent-pages* API.
It can be used to create custom page types that display :class:`~fluent_contents.models.ContentItem` objects.

The following parts are provided:

* The admin class; :class:`.admin.FluentContentsPageAdmin`
* The page type model: :class:`.models.FluentContentsPage`
* The plugin class: :class:`.page_type_plugins.FluentContentsPagePlugin`

These classes can be imported from their respective subpackages::

    from fluent_pages.integration.fluent_contents.admin import FluentContentsPageAdmin
    from fluent_pages.integration.fluent_contents.models import FluentContentsPage
    from fluent_pages.integration.fluent_contents.page_type_plugins import FluentContentsPagePlugin
"""

# There used to be more imports here, but that turned out to be a really bad idea.
# Exposing the model, plugin and admin in one __init__ package means importing the admin,
# and potentially triggering circular imports because of that (e.g. get_user_model(), load all apps)
from .models import FluentContentsPage
