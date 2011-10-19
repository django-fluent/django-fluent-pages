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

Using the custom dashboard
--------------------------

The CMS has a custom admin dashboard, which can be enabled optionally.
Include these settings::

    ADMIN_TOOLS_INDEX_DASHBOARD = 'ecms_dashboard.dashboard.EcmsIndexDashboard'
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'ecms_dashboard.dashboard.EcmsAppIndexDashboard'
    ADMIN_TOOLS_MENU = 'ecms_dashboard.menu.EcmsMenu'
    ECMS_DASHBOARD_APP_ICONS = {}

The ECMS_DASHBOARD_APP_ICONS is a dictionary that allows you to define extra icons
for your own modules, and overwrite default settings. For example::

    ECMS_DASHBOARD_APP_ICONS = {
        'auth/user': settings.MEDIA_URL + "icons/user.png"
    }

The icon is expected to be 48x48 pixels.

