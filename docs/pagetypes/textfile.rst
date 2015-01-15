.. _textfile:

The textfile page type
======================

The *textfile* allows adding a URL node that displays plain text.

  .. image:: /images/pagetypes/textfile-admin.*
     :width: 771px
     :height: 554px


This page type serves as simple demo, and can also be used to add a
custom ``robots.txt``, `humans.txt <http://humanstxt.org/>`_ file or ``README`` file to the page tree.


.. note::

    Currently, it's still required to use the "Override URL" field in the form
    to include a file extension, as the "Slug" field does not allow this.


Installation
------------

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_pages.pagetypes.textfile',
    )
