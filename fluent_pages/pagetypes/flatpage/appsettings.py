from django.conf import settings

# Purposefully using the same variable names as fluent_contents.plugins.text
FLUENT_TEXT_CLEAN_HTML = getattr(settings, "FLUENT_TEXT_CLEAN_HTML", False)
FLUENT_TEXT_SANITIZE_HTML = getattr(settings, "FLUENT_TEXT_SANITIZE_HTML", False)
