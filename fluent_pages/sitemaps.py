from django.contrib.sitemaps import Sitemap
from fluent_pages.models import UrlNode

class PageSitemap(Sitemap):
    """
    The sitemap definition for the pages created with django-fluent-pages.
    """
    def items(self):
        return UrlNode.objects.published().non_polymorphic()

    def lastmod(self, urlnode):
        """Return the last modification of the page."""
        return urlnode.last_modified

    def location(self, urlnode):
        """Return url of a page."""
        return urlnode.url
