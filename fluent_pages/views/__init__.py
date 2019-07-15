"""
All views of the CMS
"""
from .dispatcher import CmsPageAdminRedirect, CmsPageDispatcher
from .mixins import CurrentPageMixin, CurrentPageTemplateMixin
from .seo import RobotsTxtView

__all__ = (
    "CmsPageDispatcher",
    "CmsPageAdminRedirect",
    "CurrentPageMixin",
    "CurrentPageTemplateMixin",
    "RobotsTxtView",
)
