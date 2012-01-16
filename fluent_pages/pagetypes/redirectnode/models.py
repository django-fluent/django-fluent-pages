from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_pages.models import Page


class RedirectNode(Page):
    """
    A redirect node
    """
    REDIRECT_TYPE_CHOICES = (
        (302, _("Normal redirect")),
        (301, _("Permanent redirect (for SEO ranking)")),
        # Currently using status codes, however, it is perfectly possible
        # to add Refresh-header redirects later, with a temporary message in between.
    )

    new_url = models.URLField(_("New URL"))
    redirect_type = models.IntegerField(_("Redirect type"), choices=REDIRECT_TYPE_CHOICES, default=302, help_text=_("Use 'normal redirect' unless you want to transfer SEO ranking to the new page."))

    class Meta:
        verbose_name = _("Redirect")
        verbose_name_plural = _("Redirects")
