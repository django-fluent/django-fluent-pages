"""
Overview of all settings which can be customized.
"""
from django.conf import settings

ECMS_CLEAN_HTML = getattr(settings, 'ECMS_CLEAN_HTML', False)
ECMS_SANITIZE_HTML = getattr(settings, 'ECMS_SANITIZE_HTML', False)



# Test dependencies for settings that require html5lib or pytidylib
if ECMS_CLEAN_HTML:
    from django_wysiwyg import clean_html
    clean_html("<div>test</div>")
if ECMS_SANITIZE_HTML:
    from django_wysiwyg import sanitize_html
    sanitize_html("<b><script>alert(1)</script></b>")
