"""
All views of the CMS
"""
from fluent_pages.views.dispatcher import CmsPageDispatcher, CmsPageAdminRedirect
from fluent_pages.views.mixins import CurrentPageMixin, CurrentPageTemplateMixin

__all__ = (
    'CmsPageDispatcher',
    'CmsPageAdminRedirect',
    'CurrentPageMixin',
    'CurrentPageTemplateMixin',
)
