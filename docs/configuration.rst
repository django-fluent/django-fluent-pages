.. _configuration:

Configuration
=============

A quick overview of the available settings:

.. code-block:: python

    FLUENT_PAGES_BASE_TEMPLATE = "fluent_pages/base.html"

    FLUENT_PAGES_TEMPLATE_DIR = TEMPLATE_DIRS[0]

    FLUENT_PAGES_RELATIVE_TEMPLATE_DIR = True


.. _FLUENT_PAGES_BASE_TEMPLATE:

FLUENT_PAGES_BASE_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~

The name of the base template. This setting can be overwritten to point all templates to another base template.
This can be used for the :ref:`Flat page <flatpage>` page type.


.. _FLUENT_PAGES_TEMPLATE_DIR:

FLUENT_PAGES_TEMPLATE_DIR
~~~~~~~~~~~~~~~~~~~~~~~~~

The template directory where the "Layouts" model can find templates.
By default, this is the first path in ``TEMPLATE_DIRS``.


.. _FLUENT_PAGES_RELATIVE_TEMPLATE_DIR:

FLUENT_PAGES_RELATIVE_TEMPLATE_DIR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whether template paths are stored as absolute or relative paths.
This defaults to relative paths.
