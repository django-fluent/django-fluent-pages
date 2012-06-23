"""
Small URLField wrapper to support ``cmsfields.models.CmsUrlField`` if it's available.
"""
from django.conf import settings
from django.db import models


# subclassing here so South migrations detect a single class.
if 'cmsfields' in settings.INSTALLED_APPS:
    from cmsfields.models import CmsUrlField
    class UrlField(CmsUrlField):
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
