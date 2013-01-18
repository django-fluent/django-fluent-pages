from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_pages.models import HtmlPage


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
