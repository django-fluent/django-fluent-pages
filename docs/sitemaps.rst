.. _sitemaps:

Sitemaps integration
====================

The pages can be included in the sitemap that :mod:`django.contrib.sitemaps` provides.
This makes it easier for search engines to index all pages.

Add the following in :file:`urls.py`:

.. code-block:: python

    from fluent_pages.sitemaps import PageSitemap

    sitemaps = {
        'pages': PageSitemap,
    }

    urlpatterns += patterns('',
        url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    )

The :mod:`django.contrib.sitemaps` should be included in the ``INSTALLED_APPS`` off course:

.. code-block:: python

    INSTALLED_APPS += (
        'django.contrib.sitemaps',
    )

The pages should now be visible in the ``sitemap.xml``.

Note that the :file:`robots.txt` file should point to the sitemap with the full domain name included::

    Sitemap: http://full-website-domain/sitemap.xml
