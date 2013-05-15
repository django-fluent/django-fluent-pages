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
        from django.core.management.commands.compilemessages import compile_messages
        compile_messages(sys.stderr)
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
        'django-mptt>=0.5.4',
        'django-polymorphic-tree>=0.8.6',
        'django-tag-parser>=1.0.0',
    ],
    requires=[
        'Django (>=1.3)',   # Using staticfiles
    ],
    extras_require={
        'flatpage': ['django-wysiwyg>=0.5.1'],
        'fluentpage': ['django-fluent-contents>=0.8.4'],
        'redirectnode': ['django-any-urlfield>=1.0.1'],
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
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
