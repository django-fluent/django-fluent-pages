"""
Overview of all settings which can be customized.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from parler import appsettings as parler_appsettings
from parler.utils.i18n import normalize_language_code, is_supported_django_language
import os

FLUENT_PAGES_BASE_TEMPLATE = getattr(settings, "FLUENT_PAGES_BASE_TEMPLATE", 'fluent_pages/base.html')
FLUENT_PAGES_TEMPLATE_DIR = getattr(settings, 'FLUENT_PAGES_TEMPLATE_DIR', settings.TEMPLATE_DIRS[0] if settings.TEMPLATE_DIRS else None)
FLUENT_PAGES_RELATIVE_TEMPLATE_DIR = getattr(settings, 'FLUENT_PAGES_RELATIVE_TEMPLATE_DIR', True)

FLUENT_PAGES_DEFAULT_IN_NAVIGATION = getattr(settings, 'FLUENT_PAGES_DEFAULT_IN_NAVIGATION', True)

# Note: the default language setting is used during the migrations
FLUENT_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_DEFAULT_LANGUAGE_CODE', parler_appsettings.PARLER_DEFAULT_LANGUAGE_CODE)
FLUENT_PAGES_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_PAGES_DEFAULT_LANGUAGE_CODE', FLUENT_DEFAULT_LANGUAGE_CODE)
FLUENT_PAGES_LANGUAGES = getattr(settings, 'FLUENT_PAGES_LANGUAGES', parler_appsettings.PARLER_LANGUAGES)

FLUENT_PAGES_PARENT_ADMIN_MIXIN = getattr(settings, 'FLUENT_PAGES_PARENT_ADMIN_MIXIN', None)
FLUENT_PAGES_CHILD_ADMIN_MIXIN = getattr(settings, 'FLUENT_PAGES_CHILD_ADMIN_MIXIN', None)

if not FLUENT_PAGES_TEMPLATE_DIR:
    raise ImproperlyConfigured("The setting 'FLUENT_PAGES_TEMPLATE_DIR' or 'TEMPLATE_DIRS[0]' need to be defined!")
else:
    # Clean settings
    FLUENT_PAGES_TEMPLATE_DIR = FLUENT_PAGES_TEMPLATE_DIR.rstrip('/') + '/'

    # Test whether the template dir for page templates exists.
    settingName = 'TEMPLATE_DIRS[0]' if not hasattr(settings, 'FLUENT_PAGES_TEMPLATE_DIR') else 'FLUENT_PAGES_TEMPLATE_DIR'
    if not os.path.isabs(FLUENT_PAGES_TEMPLATE_DIR):
        raise ImproperlyConfigured("The setting '{0}' needs to be an absolute path!".format(settingName))
    if not os.path.exists(FLUENT_PAGES_TEMPLATE_DIR):
        raise ImproperlyConfigured("The path '{0}' in the setting '{1}' does not exist!".format(FLUENT_PAGES_TEMPLATE_DIR, settingName))


# Clean settings
FLUENT_PAGES_DEFAULT_LANGUAGE_CODE = normalize_language_code(FLUENT_PAGES_DEFAULT_LANGUAGE_CODE)

def _clean_languages():
    if not is_supported_django_language(FLUENT_PAGES_DEFAULT_LANGUAGE_CODE):
        raise ImproperlyConfigured("FLUENT_PAGES_DEFAULT_LANGUAGE_CODE '{0}' does not exist in LANGUAGES".format(FLUENT_PAGES_DEFAULT_LANGUAGE_CODE))

    FLUENT_PAGES_LANGUAGES.setdefault('default', {})
    defaults = FLUENT_PAGES_LANGUAGES['default']
    defaults.setdefault('code', FLUENT_PAGES_DEFAULT_LANGUAGE_CODE)
    defaults.setdefault('hide_untranslated', False)
    defaults.setdefault('fallback', FLUENT_PAGES_DEFAULT_LANGUAGE_CODE)

    for site_id, lang_choices in FLUENT_PAGES_LANGUAGES.iteritems():
        if site_id == 'default':
            continue

        if not isinstance(lang_choices, (list, tuple)):
            raise ImproperlyConfigured("FLUENT_PAGES_LANGUAGES[{0}] should be a tuple of language choices!".format(site_id))
        for i, choice in enumerate(lang_choices):
            if not is_supported_django_language(choice['code']):
                raise ImproperlyConfigured("FLUENT_PAGES_LANGUAGES[{0}][{1}]['code'] does not exist in LANGUAGES".format(site_id, i))
            choice.setdefault('fallback', defaults['fallback'])
            choice.setdefault('hide_untranslated', defaults['hide_untranslated'])

_clean_languages()


def get_language_settings(language_code, site_id=None):
    """
    Return the language settings for the current site
    """
    if site_id is None:
        site_id = settings.SITE_ID

    for lang_dict in FLUENT_PAGES_LANGUAGES.get(site_id, ()):
        if lang_dict['code'] == language_code:
            return lang_dict

    return FLUENT_PAGES_LANGUAGES['default']
