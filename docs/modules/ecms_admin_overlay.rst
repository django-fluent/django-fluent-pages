.. _ecms_admin_overlay:

The ecms_admin_overlay module
=============================

The ``ecms_admin_overlay`` module adds a frontend toolbar when a staff member is logged in.
This makes it easy to return to the backend, or edit the current page.

The frontend overlay is built on top of `django-admin-overlay <https://github.com/edoburu/django-admin-overlay>`_.


Installation
------------

Since the module is based on `django-admin-overlay`, it needs both modules in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'ecms_admin_overlay',
        'admin_overlay',
    )

    MIDDLEWARE_CLASSES = (
        # other classes...

        'ecms_admin_overlay.middleware.EcmsAdminOverlayMiddleware',

        # other classes...
    )

The ``admin_overlay`` module provide the generic functionality,
the ``ecms_admin_overlay`` module customizes the layout for CMS specific actions.


Customization
-------------

The :class:`admin_overlay.middleware.AdminOverlayMiddleware` and :class:`ecms_admin_overlay.middleware.EcmsAdminOverlayMiddleware`
classes are designed to be overwritten by subclasses. To customize the layout, there are several options:

* Override the templates
* Extend the middleware class, and use that class instead.

For example:

.. code-block:: python

    class CustomAdminOverlayMiddleware(EcmsAdminOverlayMiddleware):
        head_end_template   = "custom_admin_overlay/head_end.html"
        body_start_template = "custom_admin_overlay/body_start.html"
        body_end_template   = "custom_admin_overlay/body_end.html"

        def can_show_overlay(self):
            return super(CustomEcmsAdminOverlayMiddleware, self).can_show_overlay() and mycheck()

For more information, see the brief documentation of `django-admin-overlay <https://github.com/edoburu/django-admin-overlay/blob/master/README.rst>`_.

