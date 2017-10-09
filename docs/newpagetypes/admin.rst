.. _newplugins-admin:

Customizing the admin interface
===============================

The admin rendering of a page type is fully customizable.

.. versionchanged:: 1.2

    It's no longer necessary to define the ``model_admin`` attribute.
    Registering the custom admin class instead using ``admin.site.register()``
    or the ``@admin.register()`` decorator.

.. code-block:: python

    @page_type_pool.register
    class ProductCategoryPagePlugin(PageTypePlugin):
        """"
        A new page type plugin that binds the rendering and model together.
        """
        model = ProductCategoryPage
        render_template = "products/productcategorypage.html"

        model_admin = ProductCategoryPageAdmin  # only required for fluent-pages 1.1 and below.


The admin class needs to inherit from one of the following classes:

* :class:`fluent_pages.admin.PageAdmin`
* :class:`fluent_pages.admin.HtmlPageAdmin` - in case the model extends from :class:`~fluent_pages.models.HtmlPage`
* :class:`fluent_pages.pagetypes.fluentpage.admin.FluentPageAdmin`  - in case the model extends from :class:`~fluent_pages.pagetypes.fluentpage.models.FluentPageBase`

The admin can be used to customize the "add" and "edit" fields for example:

.. code-block:: python

    from django.contrib import admin
    from fluent_pages.admin import PageAdmin
    from .models import ProductCategoryPage


    @admin.register(ProductCategoryPage)
    class ProductCategoryPageAdmin(PageAdmin):
        raw_id_fields = PageAdmin.raw_id_fields + ('product_category',)


Despire being registered in the admin, the model won't show up in the index page.
The "list" page is never used, as this is rendered by the main :class:`~fluent_pages.admin.PageAdmin` class.
Only the "add" and "edit" page are exposed by the :class:`~fluent_pages.admin.PageAdmin` class too.


Customizing fieldsets
---------------------

To deal with model inheritance, the fieldsets are not set in stone in the :attr:`~django.contrib.admin.ModelAdmin.fieldsets` attribute.
Instead, the fieldsets are created dynamically using the the :attr:`~fluent_pages.admin.PageAdmin.base_fieldsets` value as starting point.
Any unknown fields (e.g. added by derived models) will be added to a separate "Contents" fieldset.

The default layout of the :class:`~fluent_pages.admin.PageAdmin` class is:

.. code-block:: python

    base_fieldsets = (
        PageAdmin.FIELDSET_GENERAL,
        PageAdmin.FIELDSET_MENU,
        PageAdmin.FIELDSET_PUBLICATION,
    )

The default layout of the :class:`~fluent_pages.admin.HtmlPageAdmin` is:

.. code-block:: python

    base_fieldsets = (
        HtmlPageAdmin.FIELDSET_GENERAL,
        HtmlPageAdmin.FIELDSET_SEO,
        HtmlPageAdmin.FIELDSET_MENU,
        HtmlPageAdmin.FIELDSET_PUBLICATION,
    )

The title of the custom "Contents" fieldset is configurable with the :attr:`~fluent_pages.admin.PageAdmin.extra_fieldset_title` attribute.


Customizing the form
--------------------

Similar to the :attr:`~fluent_pages.admin.PageAdmin.base_fieldsets` attribute,
there is a :attr:`~fluent_pages.admin.PageAdmin.base_form` attribute to use for the form.

Inherit from the :class:`~fluent_pages.admin.PageAdminForm` class to create a custom form,
so all base functionality works.
