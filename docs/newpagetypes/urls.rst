.. newpagetypes-urls:

Adding custom URLs
==================

Page types can provide custom URL patterns.
These URL patterns are relative to the place where the page is added to the page tree.

This feature is useful for example to:

* Have a "Shop" page type where all products are sub pages.
* Have a "Blog" page type where all articles are displayed below.

To use this feature, provide a URLconf or an inline :func:`~django.conf.urls.patterns` list in the page type plugin.


Basic example
-------------

To have a plugin with custom views, add the :attr:`~fluent_pages.extensions.PageTypePlugin.urls` attribute:

.. code-block:: python

    @page_type_pool.register
    class ProductCategoryPagePlugin(PageTypePlugin):
        # ...

        urls = patterns('myshop.views',
            url('^(?P<slug>[^/]+)/$', 'product_details'),
        )


The view is just a plain Django view:

.. code-block:: python

    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404, render
    from myshop.models import Product

    def product_details(request, slug):
        product = get_object_or_404(Product, slug=slug)
        return render(request, 'products/product_details.html', {
            'product': product
        })

Other custom views can be created in the same way.


Resolving URLs
--------------

The URLs can't be resolved using the standard :func:`~django.urls.reverse` function unfortunately.
The main reason is that it caches results internally for the lifetime of the WSGI container,
meanwhile pages may be rearranged by the admin.

Hence, a :func:`~fluent_pages.urlresolvers.app_reverse` function is available.
It can be used to resolve the product page:

.. code-block:: python

    from fluent_pages.urlresolvers import app_reverse

    app_reverse('product_details', kwargs={'slug': 'myproduct'})

In templates, there is an ``appurl`` tag which accomplishes the same effect:

.. code-block:: html+django

    {% load appurl_tags %}

    <a href="{% appurl 'product_details' slug='myproduct' %}">My Product</a>

.. seealso::

    The `example application <example>`_ in the source demonstrates this feature.


Compatibility with regular URLconf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An application can provide a standard :file:`urls.py` for regular Django support,
and still support page type URLs too. For this special case,
the :func:`~fluent_pages.urlresolvers.mixed_reverse` function is available.
It attemps to resolve the view in the standard URLconf first,
and falls back to :func:`~fluent_pages.urlresolvers.app_reverse` if the view is not found there.

A ``mixedurl`` template tag has to be included in the application itself. Use the following code as example:

.. code-block:: python

    @register.tag
    def mixedurl(parser, token):
        if 'fluent_pages' in settings.INSTALLED_APPS:
            from fluent_pages.templatetags.appurl_tags import appurl
            return appurl(parser, token)
        else:
            from django.templatetags.future import url
            return url(parser, token)


.. seealso::

    The django-fluent-blogs_ application uses this feature to optionally integrate the blog articles to the page tree.


.. _django-fluent-blogs: https://github.com/django-fluent/django-fluent-blogs
.. _example: https://github.com/django-fluent/django-fluent-pages/tree/master/example
