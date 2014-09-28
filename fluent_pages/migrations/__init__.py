from django.conf import settings
try:
    from django.db import migrations
except ImportError:
    # South 1.0 also reads the south_migrations folder.
    # Otherwise, you'd have to set SOUTH_MIGRATION_MODULES for all apps.
    raise DeprecationWarning("Please use South 1.0 to migrate django-fluent-pages")
