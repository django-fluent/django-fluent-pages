from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecms.models import CmsPageItem

class RawHtmlItem(CmsPageItem):
    html = models.TextField(_('HTML code'))

    class Meta:
        verbose_name = _('Raw HTML')
        verbose_name_plural = _('Raw HTML')
