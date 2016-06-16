.. _flatpage:

The flatpage page type
======================

The *flatpage* provides a simple page type with a WYSIWYG ("What You See is What You Get") editor.

  .. image:: /images/pagetypes/flatpage-admin.*
     :width: 756px
     :height: 610px

The WYSIWYG editor is provided by django-wysiwyg_, making it possible to switch to any WYSIWYG editor of your choice.

.. note::

    This page type may seem a bit too simply for your needs.
    However, in case additional fields are needed, feel free to create a different page type yourself.
    This page type can serve as canonical example.


Installation
------------

Install the dependencies via *pip*::

    pip install django-fluent-pages[flatpage]

This installs the django-wysiwyg_ package.

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_pages.pagetypes.flatpage',
        'django_wysiwyg',
    )


Using CKEditor
~~~~~~~~~~~~~~

To use CKEditor_, install django-ckeditor_::

    pip install django-ckeditor

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'ckeditor',
    )

    DJANGO_WYSIWYG_FLAVOR = "ckeditor"


Using TinyMCE
~~~~~~~~~~~~~

To use TinyMCE_, install django-tinymce_::

    pip install django-tinymce

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'tinymce',
    )

    DJANGO_WYSIWYG_FLAVOR = "tinymce"    # or "tinymce_advanced"


Using Redactor
~~~~~~~~~~~~~~

To use Redactor_, tell django-wysiwyg_ where to find the static files.
This is done on purpose to respect the commercial license.

.. code-block:: python

    DJANGO_WYSIWYG_FLAVOR = "redactor"
    DJANGO_WYSIWYG_MEDIA_URL = "/static/vendor/imperavi/redactor/"


Template layout
---------------

To integrate the output of the page into your website design, overwrite :file:`fluent_pages/base.html`.
The following blocks have to be mapped to your website theme base template:

* **title**: the sub title to display in the ``<title>`` tag.
* **content**: the content to display in the ``<body>`` tag.
* **meta-description** - the ``value`` of the meta-description tag.
* **meta-keywords** - the ``value`` for the meta-keywords tag.

In case your website base template uses different names for those blocks, create a :file:`fluent_pages/base.html` file to map the names:

.. code-block:: html+django

    {% extends "pages/base.html" %}

    {% block head-title %}{% block title %}{% endblock %}{% endblock %}

    {% block main %}{% block content %}{% endblock %}{% endblock %}


Further output tuning
~~~~~~~~~~~~~~~~~~~~~

The name of the base template can also be changed using the :ref:`FLUENT_PAGES_BASE_TEMPLATE` setting.
The page type itself is rendered using :file:`fluent_pages/pagetypes/flatpage/default.html`,
which extends the :file:`fluent_pages/base.html` template.


Configuration settings
----------------------

The following settings are available:

.. code-block:: python

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

    FLUENT_TEXT_CLEAN_HTML = True
    FLUENT_TEXT_SANITIZE_HTML = True


DJANGO_WYSIWYG_FLAVOR
~~~~~~~~~~~~~~~~~~~~~

The ``DJANGO_WYSIWYG_FLAVOR`` setting defines which WYSIWYG editor will be used.
As of django-wysiwyg_ 0.5.1, the following editors are available:

* **ckeditor** - The CKEditor_, formally known as FCKEditor.
* **redactor** - The Redactor_ editor (requires a license).
* **tinymce** - The TinyMCE_ editor, in simple mode.
* **tinymce_advanced** - The TinyMCE_ editor with many more toolbar buttons.
* **yui** - The YAHOO_ editor (the default)
* **yui_advanced** - The YAHOO_ editor with more toolbar buttons.

Additional editors can be easily added, as the setting refers to a set of templates names:

* django_wysiwyg/**flavor**/includes.html
* django_wysiwyg/**flavor**/editor_instance.html

For more information, see the documentation of django-wysiwyg_
about `extending django-wysiwyg <https://django-wysiwyg.readthedocs.io/en/latest/extending.html>`_.


FLUENT_TEXT_CLEAN_HTML
~~~~~~~~~~~~~~~~~~~~~~

If ``True``, the HTML tags will be rewritten to be well-formed.
This happens using either one of the following packages:

* html5lib_
* pytidylib_


FLUENT_TEXT_SANITIZE_HTML
~~~~~~~~~~~~~~~~~~~~~~~~~

if ``True``, unwanted HTML tags will be removed server side using html5lib_.



.. _CKEditor: http://ckeditor.com/
.. _Redactor: http://redactorjs.com/
.. _TinyMCE: http://www.tinymce.com/
.. _YAHOO: http://developer.yahoo.com/yui/editor/
.. _django-ckeditor: https://github.com/shaunsephton/django-ckeditor
.. _django-tinymce: https://github.com/aljosa/django-tinymce
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
.. _html5lib: http://code.google.com/p/html5lib/
.. _pytidylib: http://countergram.com/open-source/pytidylib
