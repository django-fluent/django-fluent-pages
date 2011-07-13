"""
The rendering support of the markup plugin.

This simply re-uses Django's template filters to do the formatting,
"""
from __future__ import absolute_import
from django.core.exceptions import ImproperlyConfigured
from django.contrib.markup.templatetags import markup
from django.utils.safestring import SafeData
from ecms_plugins.markup import appsettings


# Copy, and allow adding more options.
SUPPORTED_LANGUAGES = dict(markup.register.filters.iteritems())
LANGUAGE_NAMES = [(n, n) for n in SUPPORTED_LANGUAGES.keys()]


def render_text(text, language=None):
    """
    Render the text, reuses the template filters provided by Django.
    """
    # Get the filter
    filter = SUPPORTED_LANGUAGES.get(language or appsettings.ECMS_MARKUP_LANGUAGE)
    if not filter:
        raise ImproperlyConfigured("markup filter does not exist: %s. Valid options are: %s" % (
            appsettings.ECMS_MARKUP_LANGUAGE, SUPPORTED_LANGUAGES.keys()
        ))

    # Convert. The Django markup filters return the literal string on ImportErrors
    markup = filter(text)
    if not isinstance(markup, SafeData):
        raise ImproperlyConfigured("The required packages for the '%s' filter are not intalled!" % language)

    return markup
