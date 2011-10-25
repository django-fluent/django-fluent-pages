.. _ecms_plugins.text:

The ecms_plugins.text module
============================

The `text` plugin provides a standard WYSSIWYG ("What You See is What You Get")
editor in the administration panel, to add HTML contents to the page.

The plugin is built on top of `django-wysiwyg <https://github.com/pydanny/django-wysiwyg>`_, making it possible
to switch to any WYSIWYG editor of your choice.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'ecms_plugins.text',
        'django_wysiwyg',
    )

The dependencies can be installed via `pip`::

    pip install django-wysiwyg

Configuration
-------------

The available settings are:

.. code-block:: python

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

    ECMS_CLEAN_HTML = True
    ECMS_SANITIZE_HTML = True


DJANGO_WYSIWYG_FLAVOR
~~~~~~~~~~~~~~~~~~~~~

The ``DJANGO_WYSIWYG_FLAVOR`` setting defines which WYSIWYG editor will be used.
As of django-wysiwyg 0.3, the following editors are available:

* **ckeditor**: The CKEditor, formally known as FCKEditor
* **yui**: The YAHOO editor.
* **yui_advanced**: The YAHOO editor with more toolbar buttons.

Internally, this setting refers to a set of templates names:

* django_wysiwyg/*favor*/includes.html
* django_wysiwyg/*flavor*/editor_instance.html

For more information, see the documentation of ``django_wysiwyg``
about `Extending django-wysiwyg <http://django-wysiwyg.readthedocs.org/en/latest/extending.html>`_.


ECMS_CLEAN_HTML
~~~~~~~~~~~~~~~

If ``True``, bad HTML tags will be cleaned up server side using either one of the following modules:

* ``html5lib``
* ``pytidylib``

ECMS_SANITIZE_HTML
~~~~~~~~~~~~~~~~~~

if ``True``, the HTML insecure items will be removed server side using ``html5lib``.
