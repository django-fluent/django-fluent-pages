"""
Overview of all settings which can be customized.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import os

ECMS_CLEAN_HTML = getattr(settings, 'ECMS_CLEAN_HTML', False)
ECMS_SANITIZE_HTML = getattr(settings, 'ECMS_SANITIZE_HTML', False)

ECMS_TEMPLATE_DIR = getattr(settings, 'ECMS_TEMPLATE_DIR', settings.TEMPLATE_DIRS[0] if settings.TEMPLATE_DIRS else None)
ECMS_RELATIVE_TEMPLATE_DIR = getattr(settings, 'ECMS_RELATIVE_TEMPLATE_DIR', True)



# Clean settings
ECMS_TEMPLATE_DIR = ECMS_TEMPLATE_DIR.rstrip('/') + '/'

# Test dependencies for settings that require html5lib or pytidylib
if ECMS_CLEAN_HTML:
    from django_wysiwyg.utils import clean_html
    clean_html("<div>test</div>")
if ECMS_SANITIZE_HTML:
    from django_wysiwyg.utils import sanitize_html
    sanitize_html("<b><script>alert(1)</script></b>")

# Test whether the template dir for page templates exists.
if ECMS_TEMPLATE_DIR:
    settingName = 'TEMPLATE_DIRS[0]' if not hasattr(settings, 'ECMS_TEMPLATE_DIR') else 'ECMS_TEMPLATE_DIR'
    if not os.path.isabs(ECMS_TEMPLATE_DIR):
        raise ImproperlyConfigured("The setting '{0}' needs to be an absolute path!".format(settingName))
    if not os.path.exists(ECMS_TEMPLATE_DIR):
        raise ImproperlyConfigured("The path '{0}' in the setting '{1}' does not exist!".format(ECMS_TEMPLATE_DIR, settingName))
