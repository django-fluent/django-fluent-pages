# Add parent path,
# Allow starting the app without installing the module.
import sys
from os.path import dirname, join, realpath

import django

sys.path.insert(0, dirname(dirname(realpath(__file__))))

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': dirname(__file__) + '/demo.db',
    }
}

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'en'
SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = join(dirname(__file__), "media")
MEDIA_URL = '/media/'
STATIC_ROOT = join(dirname(__file__), "static")
STATIC_URL = '/static/'

STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-#@bi6bue%#1j)6+4b&#i0g-*xro@%f@_#zwv=2-g_@n3n_kj5'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(dirname(__file__), "templates"),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
            'context_processors': (
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ),
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

FIXTURE_DIRS = (
    join(dirname(__file__), "fixtures"),
)

FLUENT_PAGES_TEMPLATE_DIR = join(dirname(__file__), "theme1", "templates")

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # The CMS
    'fluent_pages',
    'fluent_pages.pagetypes.fluentpage',
    'fluent_pages.pagetypes.redirectnode',
    'fluent_pages.pagetypes.textfile',
    'fluent_pages.pagetypes.flatpage',
    'theme1',

    # Extra apps
    'simpleshop',

    # Required dependencies
    'mptt',
    'polymorphic',
    'polymorphic_tree',
    'parler',
    'slug_preview',

    # Content for fluentpage, with plugins that have no extra configuration requirements
    'fluent_contents',
    'fluent_contents.plugins.code',
    'fluent_contents.plugins.gist',
    'fluent_contents.plugins.googledocsviewer',
    'fluent_contents.plugins.iframe',
    'fluent_contents.plugins.markup',
    'fluent_contents.plugins.rawhtml',
    'fluent_contents.plugins.text',
    'django_wysiwyg',
    'tinymce',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'  # silence system checks

#DJANGO_WYSIWYG_FLAVOR = 'yui_advanced'
DJANGO_WYSIWYG_FLAVOR = 'tinymce_advanced'
