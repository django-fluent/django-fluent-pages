.. _sitemaps:

Sitemaps integration
====================

The pages can be included in the sitemap that :mod:`django.contrib.sitemaps` provides.
This makes it easier for search engines to index all pages.

Add the following in :file:`urls.py`:

.. code-block:: python

    from fluent_pages.sitemaps import PageSitemap
    from fluent_pages.views import RobotsTxtView

    sitemaps = {
        'pages': PageSitemap,
    }

    urlpatterns += patterns('',
        url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
        url(r'^robots.txt$', RobotsTxtView.as_view()),
    )

The :mod:`django.contrib.sitemaps` should be included in the ``INSTALLED_APPS`` off course:

.. code-block:: python

    INSTALLED_APPS += (
        'django.contrib.sitemaps',
    )

The pages should now be visible in the ``sitemap.xml``.

A sitemap is referenced in the ``robots.txt`` URL.
When using the bundled :class:`~fluent_pages.views.RobotsTxtView` in the example above, this happens by default.

The contents of the ``robots.txt`` URL can be overwritten by overriding the :file:`robots.txt` template.
Note that the :file:`robots.txt` file should point to the sitemap with the full domain name included::

    Sitemap: http://full-website-domain/sitemap.xml

For more details about the ``robots.txt`` URL, see the documentation at
http://www.robotstxt.org/ and https://support.google.com/webmasters/answer/6062608?hl=en&rd=1

.. note::

    When using Nginx, verify that ``robots.txt`` is also forwarded to your Django application.

    For example, when using ``location = /robots.txt { access_log off; log_not_found off; }``,
    the request will not be forwarded to Django because this replaces the standard ``location / { .. }`` block.
