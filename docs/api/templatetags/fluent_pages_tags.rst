fluent_pages.templatetags.fluent_pages_tags
=============================================

Template tags to request fluent page content in the template.
Load this module using:

.. code-block:: html+django

    {% load fluent_pages_tags %}


The ``render_breadcrumb`` tag
---------------------------------

Render the breadcrumb of the site, starting at the current ``page``.
This function either uses the default template,
or a custom template if the ``template`` argument is provided.

.. code-block:: html+django

    {% render_breadcrumb template="fluent_pages/parts/breadcrumb.html" %}


The ``render_menu`` tag
-----------------------------------

Render the menu of the site. The ``max_depth``, ``parent`` and ``template`` arguments are optional.

.. code-block:: html+django

    {% render_menu max_depth=1 parent="/documentation/" template="fluent_pages/parts/menu.html" %}


The ``get_fluent_page_vars`` tag
-----------------------------------

Introduces the ``site`` and ``page`` variables in the template.
This can be used for pages that are rendered by a separate application.

.. code-block:: html+django

    {% get_fluent_page_vars %}