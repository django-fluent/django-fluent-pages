"""
Overview of all settings which can be customized.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import os

FLUENT_PAGES_TEMPLATE_DIR = getattr(settings, 'FLUENT_PAGES_TEMPLATE_DIR', settings.TEMPLATE_DIRS[0] if settings.TEMPLATE_DIRS else None)
FLUENT_PAGES_RELATIVE_TEMPLATE_DIR = getattr(settings, 'FLUENT_PAGES_RELATIVE_TEMPLATE_DIR', True)



# Clean settings
FLUENT_PAGES_TEMPLATE_DIR = FLUENT_PAGES_TEMPLATE_DIR.rstrip('/') + '/'


# Test whether the template dir for page templates exists.
if FLUENT_PAGES_TEMPLATE_DIR:
    settingName = 'TEMPLATE_DIRS[0]' if not hasattr(settings, 'FLUENT_PAGES_TEMPLATE_DIR') else 'FLUENT_PAGES_TEMPLATE_DIR'
    if not os.path.isabs(FLUENT_PAGES_TEMPLATE_DIR):
        raise ImproperlyConfigured("The setting '{0}' needs to be an absolute path!".format(settingName))
    if not os.path.exists(FLUENT_PAGES_TEMPLATE_DIR):
        raise ImproperlyConfigured("The path '{0}' in the setting '{1}' does not exist!".format(FLUENT_PAGES_TEMPLATE_DIR, settingName))
