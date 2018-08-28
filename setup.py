#!/usr/bin/env python
import codecs
import os
import re
import sys
from os import path

from setuptools import find_packages, setup

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
        'django-fluent-utils>=2.0',        # DRY utility code
        'django-mptt>=0.9.0',
        'django-parler>=1.9.1',
        'django-polymorphic>=1.3.1',
        'django-polymorphic-tree>=1.5',
        'django-slug-preview>=1.0.4',
        'django-tag-parser>=3.0',
        'future>=0.12.2',
        'six>=1.5.2',
        'Pillow',  # needed by ImageField
    ],
    requires=[
        'Django (>=1.10)',
    ],
    extras_require={
        'tests': [
            'django-any-urlfield>=2.6.1',
            'django-wysiwyg>=0.7.1',
            'django-fluent-contents>=2.0.4',
        ],
        'flatpage': ['django-wysiwyg>=0.7.1'],
        'fluentpage': ['django-fluent-contents>=2.0.1'],
        'redirectnode': ['django-any-urlfield>=2.6.1'],  # Needs Pickle support for translated new_url field.
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
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
