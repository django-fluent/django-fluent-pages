"""
The rendering support of the markup plugin.

This simply re-uses Django's template filters to do the formatting,
"""
from __future__ import absolute_import
from django.core.exceptions import ImproperlyConfigured
from django.contrib.markup.templatetags import markup
from ecms_plugins.markup import appsettings


# Copy, and allow adding more options.
SUPPORTED_LANGUAGES = dict(markup.register.filters.iteritems())
LANGUAGE_NAMES = [(n, n) for n in SUPPORTED_LANGUAGES.keys()]


def render_text(text, language=None):
    """
    Render the text, reuses the template filters provided by Django.
    """
    filter = SUPPORTED_LANGUAGES.get(language or appsettings.ECMS_MARKUP_LANGUAGE)
    if not filter:
        raise ImproperlyConfigured("markup filter does not exist: %s. Valid options are: %s" % (
            appsettings.ECMS_MARKUP_LANGUAGE, SUPPORTED_LANGUAGES.keys()
        ))
    return filter(text)
