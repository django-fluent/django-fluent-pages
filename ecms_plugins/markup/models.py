from __future__ import absolute_import
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecms.extensions import CmsPageItemForm
from ecms.models import CmsPageItem
from ecms_plugins.markup import appsettings, backend

_configuredlanguageName = backend.LANGUAGE_NAMES.get(appsettings.ECMS_MARKUP_LANGUAGE)


class MarkupItemForm(CmsPageItemForm):
    """
    A custom form that validates the markup.
    """
    def clean_text(self):
        try:
            backend.render_text(self.cleaned_data['text'], self.instance.language)
        except Exception, e:
            raise ValidationError("There is an error in the markup: %s" % e)
        return self.cleaned_data['text']


class MarkupItem(CmsPageItem):
    """
    A snippet of markup (restructuredtext, markdown, or textile) to display at a page.
    """

    text = models.TextField(_('markup'))

    # Store the language to keep rendering intact while switching settings.
    language = models.CharField(_('Language'), max_length=30, editable=False, default=appsettings.ECMS_MARKUP_LANGUAGE, choices=backend.LANGUAGE_CHOICES)

    class Meta:
        verbose_name = _('%s item') % _configuredlanguageName
        verbose_name_plural = _('%s items') % _configuredlanguageName
