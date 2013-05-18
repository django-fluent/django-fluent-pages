"""
Django compatibility features
"""
from django.conf import settings

__all__ = (
    'now', 'get_user_model', 'get_user_model_name',
    'patterns', 'url', 'include',
)


# The timezone support was introduced in Django 1.4, fallback to standard library for 1.3.
try:
    from django.utils.timezone import now
except ImportError:
    # Django < 1.4
    from datetime import datetime
    now = datetime.now


# Support for custom User models in Django 1.5+
try:
    from django.contrib.auth import get_user_model

    def get_user_model_name():
        return settings.AUTH_USER_MODEL
except ImportError:
    # django < 1.5
    from django.contrib.auth.models import User

    def get_user_model():
        return User

    def get_user_model_name():
        return '{0}.{1}'.format(User._meta.app_label, User._meta.object_name)


# URLs moved in Django 1.4
try:
    # Django 1.6 requires this
    from django.conf.urls import patterns, url, include
except ImportError:
    # Django 1.3 compatibility, kept in minor release
    from django.conf.urls.defaults import patterns, url, include
