"""
A set of base classes, to build custom admin pages, for your page types.

These classes are separate from the :mod:fluent_pages.admin` module,
so importing admin classes does not invoke the app registry yet.
"""

# Import trick: make the DefaultPage*Admin available first,
# so the classes imported by .overrides can actually import those from this module already.
from .pageadmin import DefaultPageParentAdmin, DefaultPageChildAdmin, PageAdminForm
from .pagelayoutadmin import PageLayoutAdmin
from .overrides import PageParentAdmin, PageChildAdmin, PageAdmin
from .htmlpageadmin import HtmlPageAdmin


__all__ = (
    'PageParentAdmin', 'DefaultPageParentAdmin',
    'PageAdmin', 'DefaultPageChildAdmin',
    'HtmlPageAdmin',
    'PageLayoutAdmin',
    'PageAdminForm'
)