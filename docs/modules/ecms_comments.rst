.. _ecms_comments:

The ecms_comments module
=============================

The ``ecms_comments`` module adds an improved admin interface for managing comments.
It replaces the standard administration screen provided
by `django.contrib.comments <https://docs.djangoproject.com/en/dev/ref/contrib/comments/>`_.


Installation
------------

Since the module is based on `django.contrib.comments`, it needs both modules in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'django.contrib.comments',
        'ecms_comments',
    )

No further confuguration is needed for the ``ecms_comments`` module.

The `django.contrib.comments` module can be further customized to display comments.
This is explained in the :ref:`commentsarea <ecms_plugins.commentsarea>` plugin.
