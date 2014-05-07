Changelog
=========

Changes in version 0.9 (dev)
----------------------------

* Added ``key`` field to allow linking to specific user-created pages (e.g. a Terms and Conditions page).
  This feature is only visible when ``FLUENT_PAGES_KEY_CHOICES`` is configured.
* Fix support for ``i18n_patterns()`` in the ``override_url`` field.
* Added ``hide_untranslated_menu_items`` setting in ``FLUENT_PAGES_LANGUAGES`` / ``PARLER_LANGUAGES``.
* Added ``page`` variable for menu items in ``PageNavigationNode``.
* Fix resolving pages under their fallback language URL when a translated URL does exist.
* Fix exception in ``PageNavigationNode.has_children``.
* Optimize queries for rendering menu's

 * nodes without children no need a query in ``PageNavigationNode.children``.
 * avoid polymorphic behavior for child menu nodes (unless the parent node was polymorphic).


Released in 0.9b1:
~~~~~~~~~~~~~~~~~~

* Added multisite support.
* Added multilingual support, using django-parler_.
* Added hooks for patching the admin; ``FLUENT_PAGES_PARENT_ADMIN_MIXIN`` and ``FLUENT_PAGES_CHILD_ADMIN_MIXIN``.
  Note that using this feature is comparable to monkey-patching, and future compatibility can't be fully guanteed.
* Added "Can change Shared fields" permission for all page types.
* Added "Can change Page layout" permission for ``fluent_pages.pagetypes.fluentpage``.
* Allow ``formfield_overrides`` to contain field names too.
* API: added ``SeoPageMixin`` model with ``meta_title``, ``meta_keywords`` and ``meta_description`` fields.
* API: renamed ``FluentPageBase`` to ``AbstractFluentPage``.
* API: added ``get_view_response`` to the ``PageTypePlugin`` class, allow adding middleware to custom views.
* API: **Backwards incompatible:** when inheriting from the abstract ``HtmlPage`` model, your app needs a South migration.
* Fixed calling ``reverse()`` on the resolved page urls.
* Dropped Django 1.3 support.


Upgrade notices:
~~~~~~~~~~~~~~~~

* When using custom page types that inherit from inherited from ``HtmlPage``, ``FluentPageBase`` or ``AbstractFluentPage``,
  please add a South migration to your application to handle the updated fields.

 * The ``keywords`` field was renamed to ``meta_keywords``.
 * The ``description`` field was renamed to ``meta_description``.
 * The ``meta_title`` field was added.
 * The South ``rename_column`` function can be used in the migration::

     db.rename_column('your_model_table', 'keywords', 'meta_keywords')
     db.rename_column('your_model_table', 'description', 'meta_description')

* API: renamed ``FluentPageBase`` to ``AbstractFluentPage``.
  The old name is still available.


Changes in version 0.8.6
------------------------

* Add ``FLUENT_PAGES_DEFAULT_IN_NAVIGATION`` setting to change the "in navigation" default value.
* Fix django-mptt_ 0.6 support.
* Fix using `{% appurl %}` for modules with multiple results.
* Widen "modification date" column, to support other languages.


Changes in version 0.8.5
------------------------

* Added intro page for empty sites.
* Support Django 1.6 transaction management.
* Fix NL translation of "Slug".
* Fix the @admin redirect for application URLs (e.g. ``/page/app-url/@admin`` should redirect to ``/page/app-url/``).
* Fix URL dispatcher for app urls when a URL prefix is used (e.g. ``/en/..``)
* Fix Django 1.5 custom user model support in migrations


Changes in version 0.8.4
------------------------

* Fix running at Django 1.6 alpha 1
* Remove filtering pages by SITE_ID in ``PageChoiceField`` as there is no proper multi-site support yet.
* Remove ``X-Object-Type`` and ``X-Object-Id`` headers as Django 1.6 removed it due to caching issues.


Changes in version 0.8.3
------------------------

* Fix circular imports for some setups that import ``fluent_pages.urlresolvers`` early.
* Fix initial south migrations, added missing dependencies.
* Fix using ``{% render_menu %}`` at 404 pages.


Changes in version 0.8.2
------------------------

* Add ``parent`` argument to ``{% render_menu %}``, to render sub menu's.
* Add ``page``, ``site`` variable in template of ``{% render_breadcrumb %}``.
* Add ``request``, ``parent`` (the parent context) variables to templates of ``{% render_breadcrumb %}`` and ``{% render_menu %}``.
* Bump version requirement of django-mptt_ to 0.5.4, earlier versions have bugs.
* Fix ``{% get_fluent_page_vars %}`` to skip the django-haystack_ ``page`` variable.
* Fix ``{% get_fluent_page_vars %}`` when a ``site`` variable is already present.
* Fix unit test suite in Django 1.3


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
.. _django-haystack: http://haystacksearch.org/
.. _django-mptt: https://github.com/django-mptt/django-mptt
.. _django-parler: https://github.com/edoburu/django-parler
.. _django-polymorphic-tree: https://github.com/edoburu/django-polymorphic-tree
.. _django-tag-parser: https://github.com/edoburu/django-tag-parser
