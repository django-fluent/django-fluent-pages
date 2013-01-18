from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_pages.models import HtmlPage
from fluent_pages.pagetypes.flatpage import appsettings
from django_wysiwyg.utils import clean_html, sanitize_html


class FlatPage(HtmlPage):
    """
    A ```FlatPage``` represents a simple HTML page.
    """
    # Allow NULL in the layout, so this system can still be made optional in the future in favor of a configuration setting.
    template_name = models.CharField(_('Layout'), max_length=200, default='fluent_pages/pagetypes/flatpage/default.html', editable=False, null=True)
    content = models.TextField(_('Content'), blank=True)

    # Other fields, such as "registration_required" are not reused,
    # because these should be implemented globally in the base page model, or a pluggable authorization layer.

    class Meta:
        verbose_name = _("Flat Page")
        verbose_name_plural = _("Flat Pages")

    def save(self, *args, **kwargs):
        # Make well-formed if requested
        if appsettings.FLUENT_TEXT_CLEAN_HTML:
            self.content = clean_html(self.content)

        # Remove unwanted tags if requested
        if appsettings.FLUENT_TEXT_SANITIZE_HTML:
            self.content = sanitize_html(self.content)

        super(FlatPage, self).save(*args, **kwargs)
