"""
Django compatibility features
"""

__all__ = (
    'now', 'get_user_model',
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
except ImportError:
    # django < 1.5
    from django.contrib.auth.models import User

    def get_user_model():
        return User
