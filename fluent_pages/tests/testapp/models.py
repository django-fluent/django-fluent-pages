from django.db import models
from fluent_pages.models import HtmlPage

class PlainTextPage(HtmlPage):
    contents = models.TextField("Contents")

    class Meta:
        verbose_name = "Plain text page"
        verbose_name_plural = "Plain text pages"
