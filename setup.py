#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import codecs
import os
import re
import sys


# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv:
    try:
        os.chdir('fluent_pages')
        try:
            from django.core.management.commands.compilemessages import compile_messages
            compile_messages(sys.stderr)
        except ImportError:
            pass
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
    license='Apache License, Version 2.0',

    install_requires=[
        'django-mptt>=0.6.0',              # Enforce Python 3 compatible versions
        'django-parler>=1.0b3',
        'django-polymorphic>=0.5.3',       # Need 0.5.3 for several upstream fixes related to forms.
        'django-polymorphic-tree>=1.0b1',  # Enforce Python 3 compatible versions
        'django-tag-parser>=2.0b1',
        'future>=0.12.2',
    ],
    requires=[
        'Django (>=1.4)',
    ],
    extras_require={
        'flatpage': ['django-wysiwyg>=0.5.1'],
        'fluentpage': ['django-fluent-contents>=1.0b1'],
        'redirectnode': ['django-any-urlfield>=2.0a1'],
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
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
