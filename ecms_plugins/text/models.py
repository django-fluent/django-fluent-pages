from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_wysiwyg.utils import clean_html, sanitize_html
from ecms.models import CmsPageItem
from ecms import appsettings


class CmsTextItem(CmsPageItem):
    """
    A snippet of HTML text to display on a page.
    """
    text = models.TextField(_('text'), blank=True)

    class Meta:
        verbose_name = _('Text item')
        verbose_name_plural = _('Text items')

    def save(self, *args, **kwargs):
        # Cleanup the HTML if requested
        if appsettings.ECMS_CLEAN_HTML:
            self.text = clean_html(self.text)
        if appsettings.ECMS_SANITIZE_HTML:
            self.text = sanitize_html(self.text)

        super(CmsPageItem, self).save(*args, **kwargs)
