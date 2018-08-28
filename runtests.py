#!/usr/bin/env python -Wd
import sys
import warnings
from os import path

import django
from django.conf import global_settings as default_settings
from django.conf import settings
from django.core.management import execute_from_command_line


# python -Wd, or run via coverage:
warnings.simplefilter('always', DeprecationWarning)

# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    path.dirname(path.abspath(django.__file__)))
)

if not settings.configured:
    module_root = path.dirname(path.realpath(__file__))

    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'django.contrib.admin',
            'django.contrib.sessions',
            'fluent_pages',
            'fluent_pages.pagetypes.flatpage',
            'fluent_pages.pagetypes.fluentpage',
            'fluent_pages.pagetypes.redirectnode',
            'fluent_pages.pagetypes.textfile',
            'fluent_pages.tests.testapp',
            'mptt',
            'parler',
            'polymorphic',
            'polymorphic_tree',
            'fluent_contents',
            'django_wysiwyg',
            'any_urlfield',
        ),
        MIDDLEWARE = (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ),
        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': (),
                'OPTIONS': {
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
                    ),
                },
            },
        ],
        TEST_RUNNER = 'django.test.runner.DiscoverRunner',
        SITE_ID = 4,
        PARLER_LANGUAGES = {
            4: (
                {'code': 'nl', 'fallback': 'en'},
                {'code': 'en'},
            ),
        },
        PARLER_DEFAULT_LANGUAGE_CODE = 'en',  # Having a good fallback causes more code to run, more error checking.
        ROOT_URLCONF = 'fluent_pages.tests.testapp.urls',
        FLUENT_PAGES_TEMPLATE_DIR = path.join(module_root, 'fluent_pages', 'tests', 'testapp', 'templates'),
    )

DEFAULT_TEST_APPS = [
    'fluent_pages',
]


def runtests():
    other_args = list(filter(lambda arg: arg.startswith('-'), sys.argv[1:]))
    test_apps = list(filter(lambda arg: not arg.startswith('-'), sys.argv[1:])) or DEFAULT_TEST_APPS
    argv = sys.argv[:1] + ['test', '--traceback'] + other_args + test_apps
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
