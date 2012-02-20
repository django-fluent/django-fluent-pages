from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.fields import PlaceholderRelation, ContentItemRelation
from fluent_pages.models import HtmlPage, PageLayout

class FluentPageBase(HtmlPage):
    """
    A ```FluentPage``` represents one HTML page of the site.
    """
    layout = models.ForeignKey(PageLayout, verbose_name=_('Layout'))

    # Access to fluent-contents via the model
    placeholder_set = PlaceholderRelation()
    contentitem_set = ContentItemRelation()

#    objects = UrlNodeManager()

    class Meta:
        abstract = True
        verbose_name = _("Page")
        verbose_name_plural = _("Page")



class FluentPage(FluentPageBase):
    """
    A ```FluentPage``` represents one HTML page of the site.
    """
    pass
