from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecms.models import CmsPageItem

class RawHtmlItem(CmsPageItem):
    html = models.TextField(_('HTML code'), help_text=_("Enter the HTML code to display, like the embed code of an online widget."))

    class Meta:
        verbose_name = _('HTML code')
        verbose_name_plural = _('HTML code')
