Changes in version 0.8.1
------------------------

* Add "Flat page" page type.
* Add support for django-any-urlfield_.
* Add ``X-Object-Type`` and ``X-Object-Id`` headers to the response in development mode (similar to django.contrib.flatpages_).
* Add Django 1.5 Custom User model support.
* Added lots of documentation.
* Moved the template tag parsing to a separate package, django-tag-parser_.
* Improve error messages on initial project setup.
* Improve ability to extend the page change_form template.
* Improve layout of *keywords* and *description* fields in the admin.
* Fixed 500 error on invalid URLs with unicode characters.
* Fixed ``app_reverse()`` function for Django 1.3.
* Fixed ``appurl`` tag for template contexts without *page* variable.
* Fixed ``NavigationNode.is_active`` property for sub menu nodes.
* Fixed ``NavigationNode.parent`` property for root node.
* Fixed ``runtests.py`` script.
* Fixed ``Page.objects.best_match_for_path()`` for pages without a slash.
* Fixed generated URL path for "file" node types in sub folders.
* Fix Django dependency in ``setup.py``, moved from ``install_requires`` to the ``requires`` section.
* Bump version of django-polymorphic-tree_ to 0.8.6 because it fixes issues with moving pages in the admin.


Version 0.8.0
-------------

First public release

* Support for custom page types.
* Optional integration with django-fluent-contents_.
* Refactored tree logic to django-polymorphic-tree_.
* Unit tests included.

.. _django-any-urlfield: https://github.com/edoburu/django-any-urlfield
.. _django.contrib.flatpages: https://docs.djangoproject.com/en/dev/ref/contrib/flatpages/
.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
.. _django-polymorphic-tree: https://github.com/edoburu/django-polymorphic-tree
.. _django-tag-parser: https://github.com/edoburu/django-tag-parser
