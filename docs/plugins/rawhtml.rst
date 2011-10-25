.. _ecms_plugins.rawhtml:

The ecms_plugins.rawhtml module
===============================

The `rawhtml` plugin allows inserting raw HTML code in the page.
This can be used for example, to insert `jQuery <http://jquery.org/>`_ snippets in a page.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'ecms_plugins.rawhtml',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.
