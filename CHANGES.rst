Changes in version 0.8.1
------------------------

* Add support for django-any-urlfield_.
* Improve error messages on initial project setup.
* Improve ability to extend the page change_form template.
* Fix 500 error on invalid URLs with unicode characters.
* Fixed ``app_reverse()`` function for Django 1.3.
* Fixed ``appurl`` tag for template contexts without *page* variable.
* Fix Django dependency in ``setup.py``, moved from ``install_requires`` to the ``requires`` section.


Version 0.8.0
-------------

First public release

* Support for custom page types.
* Optional integration with django-fluent-contents_.
* Refactored tree logic to django-polymorphic-tree_.
* Unit tests included.

.. _django-any-urlfield: https://github.com/edoburu/django-any-urlfield
.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
.. _django-polymorphic-tree: https://github.com/edoburu/django-polymorphic-tree
