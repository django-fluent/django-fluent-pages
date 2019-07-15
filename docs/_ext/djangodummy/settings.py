# Settings file to allow parsing API documentation of Django modules,
# and provide defaults to use in the documentation.
#
# This file is placed in a subdirectory,
# so the docs root won't be detected by find_packages()
import os

# Display sane URLs in the docs:
STATIC_URL = "/static/"

# Required to pass module tests
FLUENT_PAGES_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates/")

# Required by Django
SECRET_KEY = "foo"
SITE_ID = 1

INSTALLED_APPS = [
    "fluent_pages",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "mptt",
    "polymorphic",
    "polymorphic_tree",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # / will be redirected to /<locale>/
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (),
        "OPTIONS": {
            "loaders": (
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            )
        },
    }
]
