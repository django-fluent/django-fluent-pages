from __future__ import absolute_import
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecms.extensions import CmsPageItemForm, render_error
from ecms.models import CmsPageItem
from ecms_plugins.markup import appsettings, backend


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

    text = models.TextField(_('markup'), blank=True)

    # Store the language to keep rendering intact while switching settings.
    language = models.CharField(_('Language'), max_length=30, editable=False, default=appsettings.ECMS_MARKUP_LANGUAGE, choices=backend.LANGUAGE_NAMES)

    class Meta:
        verbose_name = _('Markup text item')
        verbose_name_plural = _('Markup text items')

    def render(self):
        try:
            html = backend.render_text(self.text, self.language)
        except Exception, e:
            html = render_error(e)

        # Included in a DIV, so the next item will be displayed below.
        return '<div class="markup">' + html + '</div>\n'
