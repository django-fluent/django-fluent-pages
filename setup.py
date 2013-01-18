#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import dirname, join
import sys, os

# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv:
    try:
        os.chdir('fluent_pages')
        from django.core.management.commands.compilemessages import compile_messages
        compile_messages(sys.stderr)
    finally:
        os.chdir('..')


setup(
    name='django-fluent-pages',
    version='0.8.1',
    license='Apache License, Version 2.0',

    install_requires=[
        'django-mptt>=0.5.1',
        'django-polymorphic-tree>=0.8.4',
    ],
    requires=[
        'Django (>=1.3)',   # Using staticfiles
    ],
    extras_require={
        'flatpage': ['django-wysiwyg>=0.3.0'],
        'fluentpage': ['django-fluent-contents>=0.8.4'],
        'redirectnode': ['django-any-urlfield>=1.0.1'],
    },

    description='A page tree structure to display various content in.',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-pages',
    download_url='https://github.com/edoburu/django-fluent-pages/zipball/master',

    packages=find_packages(exclude=('example*',)),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
