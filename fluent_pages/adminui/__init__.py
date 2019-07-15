"""
A set of base classes, to build custom admin pages, for your page types.

These classes are separate from the :mod:`fluent_pages.admin` module on purpose.
Custom page type plugins can inherit these classes to provide their enhanced admin interface.
If this module could be called :mod:`fluent_pages.admin`, it would invoke the app registry
and prevent any further model initialization.
"""

from .htmlpageadmin import HtmlPageAdmin
from .overrides import PageChildAdmin, PageParentAdmin

# Import trick: make the DefaultPage*Admin available first,
# so the classes imported by .overrides can actually import those from this module already.
from .pageadmin import DefaultPageChildAdmin, DefaultPageParentAdmin, PageAdminForm
from .pagelayoutadmin import PageLayoutAdmin

__all__ = (
    "PageParentAdmin",
    "DefaultPageParentAdmin",
    "PageChildAdmin",
    "DefaultPageChildAdmin",
    "HtmlPageAdmin",
    "PageLayoutAdmin",
    "PageAdminForm",
)

PageAdmin = PageChildAdmin  # noqa, older name for backwards compatibility
