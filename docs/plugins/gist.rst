.. _ecms_plugins.gist:

The ecms_plugins.gist module
============================

The `gist` plugin provides highlighting of programming code snippets (referred to as `Gists <https://gist.github.com/>`_),
which are hosted at `GitHub <http://www.github.com/>`_.

Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'ecms_plugins.gist',
    )

The plugin does not provide additional configuration options, nor does it have dependencies on other packages.
