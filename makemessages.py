#!/usr/bin/env python
import os
from os import path

import django
from django.conf import settings
from django.core.management import call_command


def main():
    if not settings.configured:
        module_root = path.dirname(path.realpath(__file__))

        settings.configure(
            DEBUG = False,
            INSTALLED_APPS = (
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sites',
                'fluent_pages',
                'mptt',
            ),
            SITE_ID = 1,
            FLUENT_PAGES_TEMPLATE_DIR = path.join(module_root, 'fluent_pages', 'tests', 'testapp', 'templates'),
        )

    django.setup()
    makemessages()


def makemessages():
    os.chdir('fluent_pages')
    call_command('makemessages', locale=('en', 'nl'), verbosity=1)

if __name__ == '__main__':
    main()
