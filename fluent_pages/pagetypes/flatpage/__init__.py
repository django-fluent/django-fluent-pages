from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

VERSION = (0, 1)

backendapp = "django_wysiwyg"

# Do some settings checks.
if backendapp not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured(
        "The '{}' application is required to use the '{}' page type.".format(
            backendapp, "flatpage"
        )
    )

try:
    import django_wysiwyg  # noqa
except ImportError:
    raise ImportError("The 'django-wysiwyg' package is required to use the 'flatpage' page type.")
