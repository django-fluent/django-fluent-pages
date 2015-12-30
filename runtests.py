#!/usr/bin/env python
import sys
import django
from django.conf import settings, global_settings as default_settings
from django.core.management import execute_from_command_line
from os import path


# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    path.dirname(path.abspath(django.__file__)))
)

if not settings.configured:
    module_root = path.dirname(path.realpath(__file__))

    settings.configure(
        DEBUG = False,  # will be False anyway by DjangoTestRunner.
        TEMPLATE_DEBUG = True,
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        TEMPLATE_LOADERS = (
            'django.template.loaders.app_directories.Loader',
        ),
        TEMPLATE_CONTEXT_PROCESSORS = tuple(default_settings.TEMPLATE_CONTEXT_PROCESSORS) + (
            'django.core.context_processors.request',
        ),
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'django.contrib.admin',
            'django.contrib.sessions',
            'fluent_pages',
            'fluent_pages.tests.testapp',
            'mptt',
            'polymorphic',
            'polymorphic_tree',
        ),
        MIDDLEWARE_CLASSES = (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ),
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner' if django.VERSION < (1, 6) else 'django.test.runner.DiscoverRunner',
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
