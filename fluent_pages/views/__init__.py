"""
All views of the CMS
"""
from .dispatcher import CmsPageDispatcher, CmsPageAdminRedirect
from .mixins import CurrentPageMixin, CurrentPageTemplateMixin
from .seo import RobotsTxtView

__all__ = (
    'CmsPageDispatcher',
    'CmsPageAdminRedirect',
    'CurrentPageMixin',
    'CurrentPageTemplateMixin',
    'RobotsTxtView',
)
