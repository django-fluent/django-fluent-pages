Introduction
============


Installation
===========

First install the module, preferably in a virtual environment::

    mkvirtualenv fluent --no-site-packages
    workon fluent
    git clone https://github.com/edoburu/django-fluent-pages.git
    cd django-fluent-pages
    pip install .

Configuration
-------------

Next, create a project which uses the CMS::

    cd ..
    django-admin.py startproject fluentdemo

It should have the following settings::

    INSTALLED_APPS += (
        # The CMS apps
        'fluent_pages',
        'fluent_contents',

        # The CMS content plugins
        'fluent_contents.plugins.text',

        # The CMS page types
        'fluent_pages.pagetypes.fluentpage',
        'fluent_pages.pagetypes.redirectnode',

        # Support libs
        'mptt',
        'django_wysiwyg',

        # enable the admin
        'django.contrib.admin',
    )

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

Note each CMS application is optional. Only ``fluent_pages`` and ``fluent_contents`` are required.
The remaining apps add additional functionality to the system,
such as the custom dashboard or a media browser.

In ``urls.py``::

    urlpatterns += patterns('',
        url(r'', include('fluent_pages.urls'))
    )

The database can be created afterwards::

    ./manage.py syncdb
    ./manage.py loaddata welcome
    ./manage.py runserver

