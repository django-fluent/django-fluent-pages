"""
Small URLField wrapper to support ``any_urlfield.models.AnyUrlField`` if it's available.
"""
from django.conf import settings
from django.db import models


# subclassing here so South migrations detect a single class.
if 'any_urlfield' in settings.INSTALLED_APPS:
    from any_urlfield.models import AnyUrlField
    class UrlField(AnyUrlField):
        pass
else:
    class UrlField(models.URLField):
        pass

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^" + __name__.replace(".", "\.") + "\.UrlField"])
