Introduction
============


Installation
===========

First install the module, preferably in a virtual environment::

    mkvirtualenv ecms --no-site-packages
    workon ecms
    git clone https://git.edoburu.nl/git/edoburu/django-ecms.git
    cd django-ecms
    python setup.py install

Configuration
-------------

Next, create a project which uses the CMS::

    cd ..
    django-admin.py startproject ecmsdemo

It should have the following settings::

    INSTALLED_APPS += (
        # The CMS apps
        'ecms',
        'ecms_admin_overlay',
        'ecms_dashboard',
        'ecms_media',

        # The CMS content plugins
        'ecms_plugins.text',

        # Support libs
        'mptt',
        'admin_overlay',
        'django_wysiwyg',

        # enable the admin
        'admin_tools',     # for staticfiles
        'admin_tools.theming',
        'admin_tools.menu',
        'admin_tools.dashboard',
        'django.contrib.admin',
    )

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

Note each CMS application is optional. Only ``ecms`` is required.
The remaining apps add additional functionality to the system,
such as the custom dashboard or a media browser.

In ``urls.py``::

    urlpatterns += patterns('',
        url(r'', include('ecms.urls'))
    )

The database can be created afterwards::

    ./manage.py syncdb
    ./manage.py loaddata welcome
    ./manage.py runserver

