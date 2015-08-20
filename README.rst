.. image::  https://travis-ci.org/edoburu/django-fluent-pages.png?branch=master
  :target: http://travis-ci.org/edoburu/django-fluent-pages
  :alt: build-status

django-fluent-pages
===================

This is a stand-alone module, which provides a flexible,
scalable CMS with custom node types, and flexible block content.

Features:

* A fully customizable page hierarchy.
* Support for multilingual websites.
* Support for multiple websites in a single database.
* Fast SEO-friendly page URLs.
* SEO optimized (meta keywords, description, title, 301-redirects, sitemaps integration).
* Plugin support for custom page types, which:

 * Integrate application logic in page trees.
 * Integrate advanced block editing (via as django-fluent-contents_).

For more details, see the documentation_ at Read The Docs.

Page tree customization
-----------------------

This module provides a page tree, where each node type can be a different model.
This allows developers like yourself to structure your site tree as you see fit. For example:

* Build a tree structure of RST pages, by defining a ``RstPage`` type.
* Build a tree with widget-based pages, by integrating django-fluent-contents_.
* Build a "product page", which exposes all products as sub nodes.
* Build a tree of a *homepage*, *subsection*, and *article* node, each with custom fields like professional CMSes have.

Each node type can have it's own custom fields, attributes and rendering.

In case you're building a custom CMS, this module might just be suited for you,
since it provides the tree for you, without bothering with anything else.
The actual page contents is defined via page type plugins.


Installation
============

First install the module, preferably in a virtual environment::

    git clone https://github.com/edoburu/django-fluent-pages.git
    cd django-fluent-pages
    pip install .

The main dependency is django-polymorphic-tree_, which is based on django-mptt_ and django-polymorphic_.
These dependencies will be automatically installed.

Configuration
-------------

Next, create a project which uses the CMS::

    cd ..
    django-admin.py startproject fluentdemo

To have a standard setup with django-fluent-contents_ integrated, use::

    INSTALLED_APPS += (
        # The CMS apps
        'fluent_pages',

        # Required dependencies
        'mptt',
        'parler',
        'polymorphic',
        'polymorphic_tree',
        'slug_preview',

        # Optional widget pages via django-fluent-contents
        'fluent_pages.pagetypes.fluentpage',
        'fluent_contents',
        'fluent_contents.plugins.text',
        'django_wysiwyg',

        # Optional other CMS page types
        'fluent_pages.pagetypes.redirectnode',

        # enable the admin
        'django.contrib.admin',
    )

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

Note each CMS application is optional. Only ``fluent_pages`` and ``mptt`` are required.
The remaining apps add additional functionality to the system.

In ``urls.py``::

    urlpatterns += patterns('',
        url(r'', include('fluent_pages.urls'))
    )

The database can be created afterwards::

    ./manage.py syncdb
    ./manage.py runserver


Custom page types
-----------------

The key feature of this module is the support for custom node types.
Take a look in the existing types at ``fluent_pages.pagetypes`` to see how it's being done.

It boils down to creating a package with 2 files:

The ``models.py`` file should define the custom node type, and any fields it has::

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from fluent_pages.models import HtmlPage
    from mysite.settings import RST_TEMPLATE_CHOICES


    class RstPage(HtmlPage):
        """
        A page that renders RST code.
        """
        rst_content = models.TextField(_("RST contents"))
        template = models.CharField(_("Template"), max_length=200, choices=RST_TEMPLATE_CHOICES)

        class Meta:
            verbose_name = _("RST page")
            verbose_name_plural = _("RST pages")

A ``page_type_plugins.py`` file that defines the metadata, and rendering::

    from fluent_pages.extensions import PageTypePlugin, page_type_pool
    from .models import RstPage


    @page_type_pool.register
    class RstPagePlugin(PageTypePlugin):
        model = RstPage
        sort_priority = 10

        def get_render_template(self, request, rstpage, **kwargs):
            return rstpage.template

A template could look like::

    {% extends "base.html" %}
    {% load markup %}

    {% block headtitle %}{{ page.title }}{% endblock %}

    {% block main %}
      <h1>{{ page.title }}</h1>

      <div id="content">
        {{ page.rst_content|restructuredtext }}
      </div>
    {% endblock %}

Et, voila: with very little code a custom CMS was just created.

Optionally, a ``model_admin`` can also be defined, to have custom field layouts or extra functionality in the *edit* or *delete* page.

Plugin configuration
~~~~~~~~~~~~~~~~~~~~

The plugin can define the following attributes:

* ``model`` - the model for the page type
* ``model_admin`` - the custom admin to use (must inherit from ``PageAdmin``)
* ``render_template`` - the template to use for rendering
* ``response_class`` - the response class (by default ``TemplateResponse``)
* ``is_file`` - whether the node represents a file, and shouldn't end with a slash.
* ``can_have_children`` - whether the node type is allowed to have child nodes.
* ``urls`` - a custom set of URL patterns for sub pages (either a module name, or ``patterns()`` result).
* ``sort_priority`` - a sorting order in the "add page" dialog.

It can also override the following functions:

* ``get_response(self, request, page, **kwargs)`` - completely redefine the response, instead of using ``response_class``, ``render_template``, etc..
* ``get_render_template(self, request, page, **kwargs)`` - return the template to render, by default this is ``render_template``.
* ``get_context(self, request, page, **kwargs)`` - return the template context for the node.

Details about these attributes is explained in the documentation_.


Application nodes
~~~~~~~~~~~~~~~~~

As briefly mentioned above, a page type can have it's own set of URL patterns, via the ``urls`` attribute.
This allows implementing page types such as a "product page" in the tree,
which automatically has all products from the database as sub pages.
The provides ``example`` module demonstrates this concept.

The URL patterns start at the full path of the page, so it works similar to a regular ``include()`` in the URLconf.
However, a page type may be added multiple times to the tree.
To resolve the URLs, there are 2 functions available:

* ``fluent_pages.urlresolvers.app_reverse()`` - this ``reverse()`` like function locates a view attached to a page.
* ``fluent_pages.urlresolvers.mixed_reverse()`` - this resolver tries ``app_reverse()`` first, and falls back to the standard ``reverse()``.

The ``mixed_reverse()`` is useful for third party applications which
can operate either stand-alone (mounted in the normal URLconf),
or operate as page type node in combination with *django-fluent-pages*.
These features are also used by django-fluent-blogs_ to provide a "Blog" page type
that can be added to a random point of the tree.


Adding pages to the sitemap
---------------------------

Optionally, the pages can be included in the sitemap.
Add the following in ``urls.py``::

    from fluent_pages.sitemaps import PageSitemap

    sitemaps = {
        'pages': PageSitemap,
    }

    urlpatterns += patterns('',
        url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    )


Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea,
please let us know as well because we will look into it.
Pull requests are welcome too. :-)


.. _documentation: http://django-fluent-pages.readthedocs.org/
.. _django.contrib.sites: https://docs.djangoproject.com/en/dev/ref/contrib/sites/
.. _django.contrib.sitemaps: https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/

.. _django-fluent-blogs: https://github.com/edoburu/django-fluent-blogs
.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
.. _django-mptt: https://github.com/django-mptt/django-mptt
.. _django-parler: https://github.com/edoburu/django-parler
.. _django-polymorphic: https://github.com/chrisglass/django_polymorphic
.. _django-polymorphic-tree: https://github.com/edoburu/django-polymorphic-tree

