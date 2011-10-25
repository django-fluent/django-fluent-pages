.. _quickstart:

Quick start guide
=================

.. note::
    This tutorial assumes you have basic knowledge of `Django <http://www.djangoproject.com>`_,
    and already know how to setup projects.
    In case you never installed a big Django project before, see the :doc:`installation` guide.

Installing django-ecms
----------------------

django-ecms requires Django version 1.3 or higher, django-mptt 0.4.2 and django-wysiwyg 0.3.
For optional dependency management, it is strongly recommended that you run the application inside a `virtualenv`.
The package can be installed with the following commands::

    cd django-ecms
    python setup.py install


Basic setup
-----------

Next, create a project which uses the CMS.
The basic CMS can be installed with the following apps::

    INSTALLED_APPS += (
        'ecms',
        'ecms_plugins.text',

        'mptt',
        'django_wysiwyg',
        'django.contrib.admin',
    )

In ``urls.py``, add::

    urlpatterns += patterns('',
        url(r'', include('ecms.urls'))
    )

Note each CMS application is optional. Only ``ecms`` and ``mptt`` are required.

Afterwards, you can setup the database, and load the initial welcome page::

    ./manage.py syncdb
    ./manage.py loaddata welcome

Advanced setup
--------------

The CMS includes more applications to add additional functionality,
such as the custom dashboard, a media browser, or different content plugins.

A more advanced configuration can be creating using::

    INSTALLED_APPS += (
        'ecms',
        'ecms_dashboard',
        'ecms_comments',
        'ecms_media',

        # optional, content plugins
        'ecms_plugins.text',
        'ecms_plugins.code',
        'ecms_plugins.gist',
        'ecms_plugins.markup',
        'ecms_plugins.rawhtml',
        'ecms_plugins.commentsarea',
        'ecms_plugins.formdesignerlink',

        # Support libs
        'mptt',
        'django_wysiwyg',
        'django.contrib.comments',
        'formdesigner',

        # enable the admin
        'admin_tools',
        'admin_tools.theming',
        'admin_tools.menu',
        'admin_tools.dashboard',
        'django.contrib.admin',
    )

    MIDDLEWARE_CLASSES = (
        ...

        'ecms_admin_overlay.middleware.EcmsAdminOverlayMiddleware',  # frontend toolbar
    )

    # App specific settings
    ADMIN_TOOLS_INDEX_DASHBOARD = 'ecms_dashboard.dashboard.EcmsIndexDashboard'
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'ecms_dashboard.dashboard.EcmsAppIndexDashboard'
    ADMIN_TOOLS_MENU = 'ecms_dashboard.menu.EcmsMenu'

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

    ECMS_CLEAN_HTML = True
    ECMS_SANITIZE_HTML = True

    ECMS_DASHBOARD_APP_ICONS = {}

    ECMS_MARKUP_LANGUAGE = 'restructuredtext'

In ``urls.py``, some extra code is also needed::

    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^admin_tools/', include('admin_tools.urls')),

        url(r'^blog/comments/', include('django.contrib.comments.urls')),
        url(r'', include('ecms.urls'))
    )

This setup adds the following features:

* A custom dashboard and menu for the administration interface.
* An administration toolbar in the frontend website.
* Additional content plugins:

 * Code highlight
 * Gist snippets (code hosted by Github)
 * reStructuredText markup
 * Raw HTML
 * Comments area, using `django.contrib.comments`.
 * Form designer, display forms build with `django-form-designer`.

* An administration interface for comments.
* A more advanced HTML editor, with code cleanup.

Most of the features are glue to existing Python or Django modules,
hence these packages also need to be installed:

* ``django-admin-tools``
* ``Pygments``
* ``docutils``
* `django-admin-overlay <http://github.com/edoburu/django-admin-overlay>`_
* `django-formdesigner <http://github.com/philomat/django-form-designer>`_

The reason all these features are optional is make them easily swappable for other implementations.
You can use a different comments module, or invert new content plugins.
It makes the CMS configurable in the way that you see fit.
Some plugins, like the commentsarea from `django.contrib.comments`, might make a bad first impression
because they have no default layout. This turns out however, to make them highly adaptable
to your design and requirements.

.. important::
    it is very important that you put the ``admin_tools`` modules **before** 
    the ``django.contrib.admin module``, because it overrides
    the default Django admin templates, and this will not work otherwise.
    The same applies for the ``admin_overlay`` module,
    it needs to be loaded before ``ecms_admin_overlay``.

django-ecms is modular, so if you want to disable a particular 
module, just remove or comment it out in your ``INSTALLED_APPS``.


Setting up the database
~~~~~~~~~~~~~~~~~~~~~~~

To set up the tables that django-ecms uses you'll need to type::

    ./manage.py syncdb

django-ecms supports `South <http://south.aeracode.org>`_, so if you
have South installed, make sure you run the following command::

    ./manage.py migrate

Initial data can be added, so the CMS opens with a welcome page::

    ./manage.py loaddata welcome

Setting up the media files
~~~~~~~~~~~~~~~~~~~~~~~~~~

The media files of django-ecms are managed by
the `staticfiles <http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_
contrib application of Django 1.3. This requires ``STATIC_ROOT`` to be set to an
empty folder (either in your project, or ``htdocs`` / ``web`` folder).


Testing your new shiny project
------------------------------

Congrats! At this point you should have a working installation.
Now you can just login to your admin site and see what changed.

For additional customization,
please read :ref:`the customization section<customization>`.

