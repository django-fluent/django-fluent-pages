"""
Special classes to extend the module; e.g. page type plugins.

The extension mechanism is provided for projects that benefit
from a tighter integration then the Django URLconf can provide.

The API uses a registration system.
While plugins can be easily detected via ``__subclasses__()``, the register approach is less magic and more explicit.
Having to do an explicit register ensures future compatibility with other API's like reversion.
"""
from .pagetypebase import PageTypePlugin
from .pagetypepool import PageTypeAlreadyRegistered, PageTypeNotFound, PageTypePool, page_type_pool


__all__ = (
    'PageTypePlugin',
    'PageTypeAlreadyRegistered',
    'PageTypeNotFound',
    'PageTypePool',
    'page_type_pool'
)
