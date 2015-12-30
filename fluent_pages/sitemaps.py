"""
This module provides integration for the :mod:`django.contrib.sitemaps <django.contrib.sitemaps>` module.
This can be done using:

.. code-block:: python

    from fluent_pages.sitemaps import PageSitemap

    sitemaps = {
        'pages': PageSitemap,
    }

    urlpatterns += [
        url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    ]
"""
from django.contrib.sitemaps import Sitemap
from fluent_pages.models import UrlNode


class PageSitemap(Sitemap):
    """
    The sitemap definition for the pages created with *django-fluent-pages*.
    It follows the API for the :mod:`django.contrib.sitemaps <django.contrib.sitemaps>` module.
    """

    def items(self):
        """
        Return all items of the sitemap.
        """
        # Note that .active_translations() can't be combined with other filters for translations__.. fields.
        return (UrlNode.objects
                .in_sitemaps()
                .non_polymorphic()
                .active_translations()
                .prefetch_related('translations')
                .order_by('level', 'translations__language_code', 'translations___cached_url')
            )

    def lastmod(self, urlnode):
        """Return the last modification of the page."""
        return urlnode.last_modified

    def location(self, urlnode):
        """Return url of a page."""
        return urlnode.url
