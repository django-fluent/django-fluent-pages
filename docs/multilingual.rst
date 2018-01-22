Multilingual support
====================

This package supports creating content in multiple languages.
This feature is based on django-parler_.
Historical anecdote: django-parler_ was created to make this CMS multilingual.

The enable multiple languages, configuring django-parler_ is sufficient.

Configuration
-------------

.. code-block:: python

    LANGUAGES = (
        ('en', _("Global Site")),
        ('en-us', _("US Site")),
        ('it', _('Italian')),
        ('nl', _('Dutch')),
        ('fr', _('French')),
        ('es', _('Spanish')),
    )

    PARLER_DEFAULT_LANGUAGE_CODE = 'en'  # defaults to LANGUAGE_CODE

    SITE_ID = None

    PARLER_LANGUAGES = {
        None: (
            # Default SITE_ID, all languages
            {'code': lang[0]} for lang in LANGUAGES
        ),
        2: (
            # SITE_ID 2: only english/french
            {'code': 'en',}
            {'code': 'fr',}
        ),
        'default': {
            # This is applied to each entry in this setting:
            'hide_untranslated': False,
            'hide_untranslated_menu_items': False,
            # 'fallback': 'en'  # set by PARLER_DEFAULT_LANGUAGE_CODE
        }
    }

There are two extra values that can be used:

* ``hide_untranslated``: if set to ``True``, untranslated pages are not accessible.
* ``hide_untranslated_menu_items``: is set to ``True``, untranslated pages are not visible in the menu.

These values can be used in the "default" section, or in each dictionary entry per site.

Accessing content
-----------------

There are several ways to expose translated content.
One way is adding a subpath in the URL by using :func:`~django.conf.urls.i18n.i18n_patterns`:

Using i18n_patterns
~~~~~~~~~~~~~~~~~~~

Add the following to ``settings.py``:

.. code-block:: python

    MIDDLEWARE_CLASSES += (
        'django.middleware.locale.LocaleMiddleware',  # or your own override/replacement
    )

Add to ``urls.py``:

.. code-block:: python

    from django.conf.urls import patterns, url
    from django.conf.urls.i18n import i18n_patterns
    from django.contrib import admin
    from fluent_pages.sitemaps import PageSitemap

    sitemaps = {
        # Place sitemaps here
        'pages': PageSitemap,
    }

    admin.autodiscover()

    urlpatterns = patterns('',
        # All URLs that should not be prefixed with the country code,
        # e.g. robots.txt or django admin.
    ) + i18n_patterns('',
        # All URLS inside the i18n_patterns() get prefixed with the country code:
        # Django admin
        url(r'^admin/', admin.site.urls),

        # SEO API's per language
        url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

        # CMS modules
        url(r'', include('fluent_pages.urls')),
    )

Using custom middleware
~~~~~~~~~~~~~~~~~~~~~~~

Nothing prevents you from writing custom middleware that sets the frontend language.
For example:

Add the following to ``settings.py``:

.. code-block:: python

    LANGUAGE_CODE = 'en'  # default, e.g. for the admin
    FRONTEND_LANGUAGE_CODE = 'de'

    MIDDLEWARE_CLASSES += (
        'mysite.middleware.FrontendLanguageMiddleware',
    )

The custom middleware code:

.. code-block:: python

    from django.conf import settings
    from django.utils import translation
    from django.urls import reverse_lazy


    class FrontendLanguageMiddleware(object):
        """
        Change the active language when visiting a frontend page.
        """
        def __init__(self):
            # NOTE: not locale aware, assuming the admin stays at a single URL.
            self._admin_prefix = reverse_lazy('admin:index', prefix='/')

        def process_request(self, request):
            if request.path_info.startswith(str(self._admin_prefix)):
                return  # Excluding the admin

            if settings.FRONTEND_LANGUAGE_CODE != settings.LANGUAGE_CODE:
                translation.activate(settings.FRONTEND_LANGUAGE_CODE)

This could even include detecting the sub-domain, and setting the language accordingly.

All queries that run afterwards read the active language setting,
and display the content is the given language.

You can take this further and make Django aware of the sub-domain in it's URLs by
overriding :django:setting:`ABSOLUTE_URL_OVERRIDES` in the settings.
The :class:`~fluent_pages.models.Page` provides a ``default_url`` attribute for this specific use-case.
You'll also have to override the sitemap, as it won't take absolute URLs into account.

.. _django-parler: https://github.com/edoburu/django-parler
