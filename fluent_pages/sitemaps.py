"""
This module provides integration for the :mod:`django.contrib.sitemaps <django.contrib.sitemaps>` module.
This can be done using:

.. code-block:: python

    from fluent_pages.sitemaps import PageSitemap

    sitemaps = {
        'pages': PageSitemap,
    }

    urlpatterns += patterns('',
        url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    )
"""
from django.contrib.sitemaps import Sitemap
from django.utils.translation import get_language
from fluent_pages import appsettings
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
        lang_dict = appsettings.get_language_settings(get_language())
        qs = UrlNode.objects.published().non_polymorphic()

        # Limit to current languages
        if not lang_dict['hide_untranslated'] and lang_dict['fallback'] != lang_dict['code']:
            qs = qs.filter(translations__language_code__in=(lang_dict['code'], lang_dict['fallback'])).distinct()
        else:
            qs = qs.filter(translations__language_code=lang_dict['code'])

        return qs.order_by('level', 'translations__language_code', 'translations___cached_url')

    def lastmod(self, urlnode):
        """Return the last modification of the page."""
        return urlnode.last_modified

    def location(self, urlnode):
        """Return url of a page."""
        return urlnode.url
