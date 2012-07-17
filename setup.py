#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-fluent-pages',
    version='0.1.0',
    license='Apache License, Version 2.0',

    install_requires=[
        'Django>=1.3.0',
        'django-mptt>=0.5.1',
        'django-polymorphic-tree>=0.8.1',
    ],
    description='A page tree structure to display various content in.',
    long_description=open('README.rst').read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-contents',
    download_url='https://github.com/edoburu/django-fluent-contents/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
