from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecms.models.pluginmodel import CmsPageItem
from . import backend, appsettings

class CodeItem(CmsPageItem):
    """
    A snippet of source code, formatted with syntax highlighting.
    """

    language = models.CharField(_('Language'), max_length=50, choices=backend.LANGUAGE_CHOICES, default=appsettings.ECMS_CODE_DEFAULT_LANGUAGE)
    code = models.TextField(_('Code'))
    linenumbers = models.BooleanField(_('Show line numbers'), default=appsettings.ECMS_CODE_DEFAULT_LINE_NUMBERS)

    class Meta:
        verbose_name = _('Sourcecode listing')
        verbose_name_plural = _('Sourcecode listings')
