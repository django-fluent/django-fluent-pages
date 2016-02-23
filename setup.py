#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import codecs
import os
import re
import sys


# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv or 'develop' in sys.argv:
    os.chdir('fluent_pages')
    try:
        from django.core import management
        management.call_command('compilemessages', stdout=sys.stderr, verbosity=1)
    except ImportError:
        if 'sdist' in sys.argv:
            raise
    finally:
        os.chdir('..')


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-fluent-pages',
    version=find_version('fluent_pages', '__init__.py'),
    license='Apache 2.0',

    install_requires=[
        'django-fluent-utils>=1.2.3',      # DRY utility code
        'django-mptt>=0.5.5',              # Still supporting Django 1.5, use mptt 0.6 for Python 3 support.
        'django-parler>=1.6.1',            # Needed for Django 1.9 compatibility
        'django-polymorphic>=0.9.1',       # Needed for Django 1.8 compatibility
        'django-polymorphic-tree>=1.2.3',  # Needed for Django 1.9 compatibility
        'django-slug-preview>=1.0.1',
        'django-tag-parser>=2.1',
        'future>=0.12.2',
        'six>=1.5.2',
    ],
    requires=[
        'Django (>=1.5)',
    ],
    extras_require={
        'flatpage': ['django-wysiwyg>=0.7.1'],
        'fluentpage': ['django-fluent-contents>=1.1'],
        'redirectnode': ['django-any-urlfield>=2.2'],  # Needs Pickle support for translated new_url field.
    },
    description='A flexible, scalable CMS with custom node types, and flexible block content.',
    long_description=read('README.rst'),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-pages',
    download_url='https://github.com/edoburu/django-fluent-pages/zipball/master',

    packages=find_packages(exclude=('example*',)),
    include_package_data=True,

    test_suite='runtests',

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Framework :: Django',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
