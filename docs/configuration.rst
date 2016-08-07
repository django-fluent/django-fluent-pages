.. _configuration:

Configuration
=============

A quick overview of the available settings:

.. code-block:: python

    FLUENT_PAGES_BASE_TEMPLATE = "fluent_pages/base.html"

    FLUENT_PAGES_TEMPLATE_DIR = TEMPLATE_DIRS[0]

    FLUENT_PAGES_RELATIVE_TEMPLATE_DIR = True

    FLUENT_PAGES_DEFAULT_IN_NAVIGATION = True

    FLUENT_PAGES_KEY_CHOICES = ()

    # Advanced
    FLUENT_PAGES_PREFETCH_TRANSLATIONS = False
    FLUENT_PAGES_FILTER_SITE_ID = True
    FLUENT_PAGES_PARENT_ADMIN_MIXIN = None
    FLUENT_PAGES_CHILD_ADMIN_MIXIN = None
    ROBOTS_TXT_DISALLOW_ALL = DEBUG


Template locations
------------------

.. _FLUENT_PAGES_BASE_TEMPLATE:

FLUENT_PAGES_BASE_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~

The name of the base template. This setting can be overwritten to point all templates to another base template.
This can be used for the :ref:`Flat page <flatpage>` page type.


.. _FLUENT_PAGES_TEMPLATE_DIR:

FLUENT_PAGES_TEMPLATE_DIR
~~~~~~~~~~~~~~~~~~~~~~~~~

The template directory where the "Layouts" model can find templates.
By default, this is the first path in ``TEMPLATE_DIRS``. It can also be set explicitly, for example:

.. code-block:: python

    FLUENT_PAGES_TEMPLATE_DIR = os.path.join(SRC_DIR, 'frontend', 'templates')


.. _FLUENT_PAGES_RELATIVE_TEMPLATE_DIR:

FLUENT_PAGES_RELATIVE_TEMPLATE_DIR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whether template paths are stored as absolute or relative paths.
This defaults to relative paths:

.. code-block:: python

    FLUENT_PAGES_RELATIVE_TEMPLATE_DIR = True


Preferences for the admin
-------------------------

.. _FLUENT_PAGES_DEFAULT_IN_NAVIGATION:

FLUENT_PAGES_DEFAULT_IN_NAVIGATION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This defines whether new pages have the "Show in Navigation" checkbox enabled by default.
It makes sense for small sites to enable it, and for larger sites to disable it:

.. code-block:: python

    FLUENT_PAGES_DEFAULT_IN_NAVIGATION = False


.. _FLUENT_PAGES_KEY_CHOICES:

FLUENT_PAGES_KEY_CHOICES
~~~~~~~~~~~~~~~~~~~~~~~~

Pages can be "tagged" to be easily found in the page tree.
Example value:

.. code-block:: python

    FLUENT_PAGES_KEY_CHOICES = (
        # Allow to tag some pages, so they can be easily found by templates.
        ('search', _("Search")),
        ('contact', _("Contact")),
        ('terms', _("Terms and Conditions")),
        ('faq', _("FAQ page")),
        ('impactmap', _("Impact map")),
    )

When this value is defined, a "Page identifier" option appears in the "Publication settings" fieldset.

Pages which are marked with an identifier can be found
using :func:`Page.objects.get_for_key() <fluent_pages.models.UrlNodeManager.get_for_key>`.


Performance optimizations
-------------------------


.. _FLUENT_PAGES_PREFETCH_TRANSLATIONS:

FLUENT_PAGES_PREFETCH_TRANSLATIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable this to prefetch all translations at a regular page.
This is useful to display a language choice menu:

.. code-block:: python

    FLUENT_PAGES_PREFETCH_TRANSLATIONS = True


SEO settings
------------

.. _ROBOTS_TXT_DISALLOW_ALL:

ROBOTS_TXT_DISALLOW_ALL
~~~~~~~~~~~~~~~~~~~~~~~

When using :class:`~fluent_pages.views.RobotsTxtView`, enable this setting for beta websites.
This makes sure such site won't be indexed by search engines.
Off course, it's recommended to add HTTP authentication to such site,
to prevent accessing the site at all.


Advanced admin settings
-----------------------


.. _FLUENT_PAGES_FILTER_SITE_ID:

FLUENT_PAGES_FILTER_SITE_ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, each :class:`~django.contrib.sites.models.Site` model has it's own page tree.
This enables the multi-site support, where you can run multiple instances with different sites.
To run a single Django instance with multiple sites, use a module such as django-multisite_.

You can disable it using this by using:

.. code-block:: python

    FLUENT_PAGES_FILTER_SITE_ID = False


.. _FLUENT_PAGES_PARENT_ADMIN_MIXIN:
.. _FLUENT_PAGES_CHILD_ADMIN_MIXIN:

FLUENT_PAGES_PARENT_ADMIN_MIXIN / FLUENT_PAGES_CHILD_ADMIN_MIXIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By setting this value, this module will insert your class in the admin.
This can be used to override methods, or provide integration other
third party applications such as django-guardian_.

* The "parent admin" handles the list display for pages.
* The "child admin" handles the edit and delete views for pages.

Example setting:

.. code-block:: python

    FLUENT_PAGES_PARENT_ADMIN_MIXIN = 'apps.auth_utils.page_admin.FluentPagesParentAdminMixin'
    FLUENT_PAGES_CHILD_ADMIN_MIXIN = 'apps.auth_utils.page_admin.FluentPagesChildAdminMixin'

Your project needs to provide those classes,
and can implement or override admin methods there.


Advanced language settings
--------------------------

The language settings are copied by default from the *django-parler* variables.
If you have to provide special settings (basically fork the settings),
you can provide the following values::

    FLUENT_DEFAULT_LANGUAGE_CODE = PARLER_DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE

    FLUENT_PAGES_DEFAULT_LANGUAGE_CODE = FLUENT_DEFAULT_LANGUAGE_CODE
    FLUENT_PAGES_LANGUAGES = PARLER_LANGUAGES


.. _django-guardian: https://github.com/lukaszb/django-guardian
.. _django-multisite: https://github.com/ecometrica/django-multisite
