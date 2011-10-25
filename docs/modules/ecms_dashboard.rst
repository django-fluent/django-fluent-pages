.. _ecms_dashboard:

The ecms_dashboard module
=========================

The ``ecms_dashboard`` module offers a custom admin dashboard, built on top of
`django-admin-tools <https://bitbucket.org/izi/django-admin-tools/wiki/Home>`_ (`docs <http://django-admin-tools.readthedocs.org/>`_).

The `django-admin-tools` provides a default mechanism to replace the standard Django
admin homepage with a widget based dashboard. The ``ecms_dashboard`` extends this,
by providing additional widgets (called "modules") which can be displayed at the homepage.


Installation
------------

To install this feature, both the `ecms_dashboard` and the `admin_tools` modules have to be to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'ecms_dashboard',

        'admin_tools',     # for staticfiles
        'admin_tools.theming',
        'admin_tools.menu',
        'admin_tools.dashboard',
        'django.contrib.admin',
    )

.. note::
    The ``admin_tools.theming`` and ``admin_tools.menu`` applications are optional.

Next, the `django-admin-tools` can be configured to use the ``ecms_dashboard`` instead, by using::

    ADMIN_TOOLS_INDEX_DASHBOARD = 'ecms_dashboard.dashboard.EcmsIndexDashboard'
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'ecms_dashboard.dashboard.EcmsAppIndexDashboard'
    ADMIN_TOOLS_MENU = 'ecms_dashboard.menu.EcmsMenu'

The admin-tools dependency can be installed via `pip`:

.. code-block:: sh

    pip install django-admin-tools    # Django 1.2

For Django 1.3, install at least 0.4.2, which at the moment of writing requires:

.. code-block:: sh

    pip install -e 'hg+http://bitbucket.org/izi/django-admin-tools/@8bcc0fba234698315335aaae1fcdfdded9e12173#egg=django_admin_tools-dev'


Available settings
------------------

The available settings are:

.. code-block:: python

  ECMS_DASHBOARD_APP_ICONS = {
      'cms/page': 'ecms_dashboard/oxygen/internet-web-browser.png',
  }

  ECMS_DASHBOARD_DEFAULT_ICON = 'ecms_dashboard/oxygen/unknown.png'

  ECMS_DASHBOARD_APP_GROUPS = (
      (_('CMS'), ('*',)),
      (_('Interactivity'), ('zinnia.*', 'django.contrib.comments.*', 'form_designer.*')),
      (_('Administration'), ('django.contrib.auth.*', 'django.contrib.sites.*', 'registration.*', 'google_analytics.*',)),
  )


ECMS_DASHBOARD_APP_ICONS
~~~~~~~~~~~~~~~~~~~~~~~~

A dictionary of the `app/model`, and the associated icon.
For a few commonly know applications, icons are already provided.
The icon paths are relative to the ``STATIC_URL`` (or ``MEDIA_URL``) defined in the settings.

Any key defined in ``settings.py`` overrides the default.

ECMS_DASHBOARD_DEFAULT_ICON
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case a suitable icon is not found, this icon is used.
The icon path is relative to the ``STATIC_URL`` (or ``MEDIA_URL``) defined in the settings.

ECMS_DASHBOARD_APP_GROUPS
~~~~~~~~~~~~~~~~~~~~~~~~~

The application groups to display at the dashboard.
Each tuple defines the title, and list of included modules.
By default, there is a section for "CMS", "Interactivity" and "Administration" filled with known Django applications.

The ``*`` selector without any application name, is special:
it functions as a catch-all for all remaining unmatched items.


Advanced customization
----------------------

For advanced dashboard or menu layouts, consider overwriting the classes
provided by the ``admin_tools.dashboard`` and ``ecms_dashboard`` modules.
These can be used in the ``ADMIN_TOOLS_INDEX_DASHBOARD``, ``ADMIN_TOOLS_APP_INDEX_DASHBOARD``, and ``ADMIN_TOOLS_MENU`` settings.
The existing modules in ``ecms_dashboard.modules`` could be reused off course.

The ``ecms_dashboard`` provides the following classes:

* :mod:`ecms_dashoard.dashboard`: the custom dashboard classes:

 * :class:`ecms_dashboard.dashboard.EcmsIndexDashboard`: the dashboard for the homepage.
 * :class:`ecms_dashboard.dashboard.EcmsAppIndexDashboard``: the dashboard for the application index page.

* :mod:`ecms_dashboard.items`: menu icons

 * :class:`ecms_dashboard.items.CmsModelList`: a model list, with strong bias of sorting CMS applications on top.
 * :class:`ecms_dashboard.items.ReturnToSiteItem`: a custom :class:`admin_tools.menu.items.MenuItem` class, with the "Return to site" link.

* :mod:`ecms_dashboard.menu`: the menu classes.

 * :class:`ecms_dashboard.menu.EcmsMenu`: a custom :class:`admin_tools.menu.Menu` implementation, which honors the ``ECMS_DASHBOARD_APP_GROUPS`` setting, and adds the `ReturnToSiteItem`.

* :mod:`ecms_dashboard.modules`: custom widgets (called "modules") to display at the dashboard.

 * :class:`ecms_dashboard.modules.PersonalModule`: a personal welcome text. It displays the ``ecms_dashboard/modules/personal.html`` template.
 * :class:`ecms_dashboard.modules.AppIconList`: a :class:`admin_tools.dashboard.modules.AppList` implementation that displays the models as icons.
 * :class:`ecms_dashboard.modules.CmsAppIconList`: a `AppIconList` variation with a strong bios towards sorting CMS applications on top.
