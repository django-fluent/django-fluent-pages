"""
Utils for translations
"""
from django.conf import settings

LANGUAGES_DICT = dict(settings.LANGUAGES)


def normalize_language_code(code):
    return code.lower().replace('_', '-')


def is_supported_django_language(language_code):
    """
    Return whether a language code is supported.
    """
    language_code = language_code.split('-')[0] # e.g. if fr-ca is not supported fallback to fr
    return language_code in LANGUAGES_DICT


def get_language_title(language_code):
    """
    Return the verbose_name for a language code.
    """
    try:
        return LANGUAGES_DICT[language_code]
    except KeyError:
        language_code = language_code.split('-')[0] # e.g. if fr-ca is not supported fallback to fr
        return LANGUAGES_DICT[language_code]
