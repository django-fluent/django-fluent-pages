"""
Settings for the code plugin.
"""
from django.conf import settings

ECMS_CODE_DEFAULT_LANGUAGE = getattr(settings, "ECMS_CODE_DEFAULT_LANGUAGE", '')
ECMS_CODE_DEFAULT_STYLE = getattr(settings, 'ECMS_CODE_DEFAULT_STYLE', 'default')
ECMS_CODE_DEFAULT_LINE_NUMBERS = getattr(settings, 'ECMS_CODE_DEFAULT_LINE_NUMBERS', False)