from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.fields import PlaceholderRelation, ContentItemRelation
from fluent_pages.models import HtmlPage, PageLayout

class FluentPageBase(HtmlPage):
    """
    A ```FluentPage``` represents one HTML page of the site.

    This class is abstract, so it's easy to reuse the same CMS functionality in your custom page types
    without introducing another table/join indirection in the database. Naturally, the same layout mechanism is used.
    In case the ``layout`` should be handled differently, please consider building a variation of this page type application.

    The API to interface with *django-fluent-contents* is public, and documented for this reason.
    In fact, this application is just a tiny bridge between the page type plugins and the *django-fluent-pages* API.
    """
    # Allow NULL in the layout, so this system can still be made optional in the future in favor of a configuration setting.
    layout = models.ForeignKey(PageLayout, verbose_name=_('Layout'), null=True)

    # Access to fluent-contents via the model
    placeholder_set = PlaceholderRelation()
    contentitem_set = ContentItemRelation()

#    objects = UrlNodeManager()

    class Meta:
        abstract = True
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")



class FluentPage(FluentPageBase):
    """
    A ```FluentPage``` represents one HTML page of the site.
    """
    pass