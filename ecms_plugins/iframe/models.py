from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecms.models import CmsPageItem
import re


def _validate_size(value):
    if not re.match(r'^\d+%?$', value):
        raise ValidationError(_("Value should be a number or percentage."))


class IframeItem(CmsPageItem):
    """
    An ``<iframe>`` that is displayed at the page..
    """
    title = models.CharField(_("Title"), max_length=300)
    src = models.URLField(_("Page URL"))
    width = models.CharField(_("Width"), max_length=10, validators=[_validate_size], default="100%", help_text=_("Specify the size in pixels, or a percentage of the container area size."))
    height = models.CharField(_("Height"), max_length=10, validators=[_validate_size], default="600", help_text=_("Specify the size in pixels."))

    class Meta:
        verbose_name = _("Iframe")
        verbose_name_plural = _("Iframes")

    def __unicode__(self):
        return self.title
