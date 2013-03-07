from django.db import models
from fluent_pages.models import Page, HtmlPage

class SimpleTextPage(HtmlPage):
    contents = models.TextField("Contents")

    class Meta:
        verbose_name = "Plain text page"
        verbose_name_plural = "Plain text pages"


class PlainTextFile(Page):
    content = models.TextField("Contents")

    class Meta:
        verbose_name = "Plain text file"
        verbose_name_plural = "Plain text files"


class WebShopPage(Page):
    class Meta:
        verbose_name = "Webshop page"
        verbose_name_plural = "Webshop pages"
