.. newpagetypes-rendering:

Customizing the frontend rendering
==================================

As displayed in the :doc:`models` page, a page type is made of two classes:

* A model class in :file:`models.py`.
* A plugin class in :file:`page_type_plugins.py`.

The plugin class renders the model instance using:

* A custom :func:`~fluent_pages.extensions.PageTypePlugin.get_response` method.

* The :attr:`~fluent_pages.extensions.PageTypePlugin.render_template` attribute,
  :func:`~fluent_pages.extensions.PageTypePlugin.get_render_template` method
  and optionally :func:`~fluent_pages.extensions.PageTypePlugin.get_context` method.

Simply stated, a plugin provides the "view" of the "page".


Simple rendering
----------------

To quickly create plugins with little to no effort, only the :attr:`~fluent_pages.extensions.PageTypePlugin.render_template` needs to be specified.
The template code receives the model object via the ``instance`` variable.

To switch the template depending on the model, the :func:`~fluent_pages.extensions.PageTypePlugin.get_render_template` method
can be overwritten instead. For example:

.. code-block:: python

    @page_type.register
    class MyPageType(PageTypePlugin):
        # ...

        def get_render_template(self, request, page, **kwargs):
            return page.template_name or self.render_template


To add more context data, overwrite the :class:`~fluent_pages.extensions.PageTypePlugin.get_context` method.


Custom rendering
----------------

Instead of only providing extra context data,
the whole :func:`~fluent_pages.extensions.PageTypePlugin.get_response` method can be overwritten as well.

The :ref:`textfile <textfile>` and :ref:`redirectnode <redirectnode>` page types use this for example:

.. code-block:: python

    def get_response(self, request, redirectnode, **kwargs):
        response = HttpResponseRedirect(redirectnode.new_url)
        response.status_code = redirectnode.redirect_type
        return response

The standard :func:`~fluent_pages.extensions.PageTypePlugin.get_response` method basically does the following:

.. code-block:: python

    def get_response(self, request, page, **kwargs):
        render_template = self.get_render_template(request, page, **kwargs)
        context = self.get_context(request, page, **kwargs)
        return self.response_class(
            request = request,
            template = render_template,
            context = context,
        )

* It takes the template from :func:`~fluent_pages.extensions.PageTypePlugin.get_render_template`.
* It uses the context provided by :func:`~fluent_pages.extensions.PageTypePlugin.get_context`.
* It uses :func:`~fluent_pages.extensions.PageTypePlugin.response_class` class to output the response.

.. note::

    The :class:`PageTypePlugin` class is instantiated once, just like the :class:`~django.contrib.admin.ModelAdmin` class.
    Unlike the Django class based views, it's not possible to store state at the local instance.
