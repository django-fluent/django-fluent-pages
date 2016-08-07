Welcome to django-fluent-pages's documentation!
===============================================

This module provides a page tree, where each node type can be a different model.
This allows you to structure your site CMS tree as you see fit. For example:

* Build a tree of flat pages, with a WYSIWYG editor.
* Build a tree with widget-based pages, by integrating django-fluent-contents_.
* Build a tree structure of RST pages, by defining a ``RstPage`` type.
* Build a tree of a *homepage*, *subsection*, and *article* node, each with custom fields like professional CMSes have.

Each node type can have it's own custom fields, attributes, URL patterns and rendering.

In case you're building a custom CMS, this module might just be suited for you,
since it provides the tree for you, without bothering with anything else.
The actual page contents is defined via page type plugins.
To get up and running quickly, consult the :ref:`quick-start guide <quickstart>`.
The chapters below describe the configuration of each specific plugin in more detail.

Preview
-------

.. image:: /images/pagetypes/fluentpage-admin.*
   :width: 756px
   :height: 726px
   :alt: django-fluent-pages admin preview


Getting started
---------------

.. toctree::
   :maxdepth: 2

   quickstart
   configuration
   templatetags
   sitemaps
   multilingual
   management


Using the page type plugins
---------------------------

.. toctree::
   :maxdepth: 2

   pagetypes/index
   newpagetypes/index


API documentation
-----------------

.. toctree::
   :maxdepth: 2

   lowlevel
   api/index
   dependencies
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _django-fluent-contents: https://github.com/django-fluent/django-fluent-contents
