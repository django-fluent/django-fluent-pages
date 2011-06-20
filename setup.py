#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-ecms',
    version='0.1.0',
    license='Apache License, Version 2.0',

    install_requires=[
        'Django>=1.3.0',
        'django-mptt>=0.4.2',
        'django-wysiwyg>=0.3.0',
    ],
    dependency_links=[
        'http://bitbucket.org/izi/django-admin-tools/get/8bcc0fba2346.tar.gz#egg=django_admin_tools-0.4.1hg',
    ],

    description='Django ECMS - The experimental/extensible/enhanced/enterprice CMS for Django projects',
    long_description=open('README.rst').read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-ecms',
    download_url='https://github.com/edoburu/django-ecms/zipball/master',

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
