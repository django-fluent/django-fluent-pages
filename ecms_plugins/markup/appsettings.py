"""
Settings for the markup part.
"""
from django.conf import settings

ECMS_MARKUP_LANGUAGE = getattr(settings, "ECMS_MARKUP_LANGUAGE", 'restructuredtext')
