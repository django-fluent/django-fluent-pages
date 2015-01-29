from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_pages.models import Page
from parler.models import TranslatedFields
from fluent_utils.softdeps.any_urlfield import AnyUrlField


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

    # Note that the UrlField can support internal links too when django-any-urlfield is installed.
    redirect_translations = TranslatedFields(
        new_url = AnyUrlField(_("New URL"), max_length=255),
        redirect_type = models.IntegerField(_("Redirect type"), choices=REDIRECT_TYPE_CHOICES, default=302, help_text=_("Use 'normal redirect' unless you want to transfer SEO ranking to the new page.")),
    )

    class Meta:
        # If this page class didn't exist as real model before,
        # it would be very tempting to turn it into a proxy:
        #proxy = True
        verbose_name = _("Redirect")
        verbose_name_plural = _("Redirects")

    # While it's very tempting to overwrite get_absolute_url() or 'url' with the new URL,
    # the consequences for caching are probably too big to cope with. Just redirect instead.
