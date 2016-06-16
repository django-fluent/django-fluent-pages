.. _redirectnode:

The redirectnode page type
==========================

The *redirectnode* allows adding a URL path that redirects the website visitor.

  .. image:: /images/pagetypes/redirectnode-admin.*
     :width: 771px
     :height: 490px


Installation
------------

Install the dependencies via *pip*::

    pip install django-fluent-pages[redirectnode]

This installs the django-any-urlfield_ package.

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_pages.pagetypes.redirectnode',
        'any_urlfield',
    )


Configuration
-------------

This page type works out of the box.

By default, the admin can choose between an "External URL" and "Page".
Other models can also be included too, as long as they have a ``get_absolute_url`` method.
Register the respective models to django-any-urlfield_:

.. code-block:: python

    from any_urlfield.models import AnyUrlField
    AnyUrlField.register_model(Article)

See the :mod:`anyurlfield:any_urlfield.models` documentation for details.



.. _django-any-urlfield: https://django-any-urlfield.readthedocs.io/en/latest/
