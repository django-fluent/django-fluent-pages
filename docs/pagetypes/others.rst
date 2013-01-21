.. _other-known-pagetypes:

Other known page types
======================

Blog page
---------

The django-fluent-blogs_ module provides a "Blog page" type, which can be used to include a "Blog" in the page tree.

To integrate it with this module, configure it using:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_blogs',
        'fluent_blogs.pagetypes.blogpage',
    )

See the documentation of django-fluent-blogs_ for details.


Open idea's
-----------

Other page types can also be written, for example:

* a "Portfolio" page type.
* a "Split test" page type.
* a "Flat page" with reStructuredText content.
* a "Web shop" page type.
* a "Subsite section" page type.

See the next chapter, :ref:`newpagetypes` to create such plugin.


.. _django-fluent-blogs: https://github.com/edoburu/django-fluent-blogs
