from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_pages.models import PageLayout
from fluent_pages.integration.fluent_contents.models import FluentContentsPage

from parler.fields import TranslatedField
from parler.models import TranslatableModel, TranslatedFieldsModel


# This all exists for backwards compatibility
# The new v0.9 method is using fluent_pages.integration.fluent_contents, instead of directly inheriting this app.
# In that way, the pagetypes are stand-alone apps again.
class AbstractFluentPage(FluentContentsPage, TranslatableModel):
    """
    A ```FluentPage``` represents one HTML page of the site.

    .. note::

        If you really like to use the ``layout`` field in our custom applications, inherit from this class.
        Otherwise, please use :class:`fluent_pages.integration.fluent_contents.models.FluentContentsPage` instead.

    This class is abstract, so it's easy to reuse the same CMS functionality in your custom page types
    without introducing another table/join indirection in the database. Naturally, the same layout mechanism is used.
    In case the ``layout`` should be handled differently, please consider building a variation of this page type application.
    """
    layout = TranslatedField(any_language=True)

    class Meta:
        abstract = True
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")


class AbstractFluentPageTranslation(TranslatedFieldsModel):

    # Allow NULL in the layout, so this system can still be made
    # optional in the future in favor of a configuration setting.
    layout = models.ForeignKey(PageLayout, verbose_name=_('Layout'), null=True)

    master = None

    class Meta:
        abstract = True
        permissions = (
            ('change_page_layout', _("Can change Page layout")),
        )


class FluentPage(AbstractFluentPage):
    """
    A ```FluentPage``` represents one HTML page of the site.
    """
    pass


class FluentPageTranslation(AbstractFluentPageTranslation):

    master = models.ForeignKey(FluentPage, related_name='page_translations')
