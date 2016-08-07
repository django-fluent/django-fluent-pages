Low-level API's
===============

This package provides internal API's, so projects can use those
to query the tree or even prefill it.

.. note::

   When using the Python shell, make sure the activate a language first.

   .. code-block:: python

        from django.conf import settings
        from django.utils.translations import activate

        activate(settings.LANGUAGE_CODE)


Query pages
-----------

When you query the general :class:`~fluent_pages.models.Page`
or :class:`~fluent_pages.models.UrlNode` model, the pages are returned in their specific type.

.. code-block:: python

    >>> from fluent_pages.models import Page
    >>> Page.objects.published()
    <Queryset [<FluentPage: Homepage>, <BlogPage: Blog>, <FluentPage: Contact>]>

To filter the results, use one of these methods:

* :meth:`~fluent_pages.models.UrlNodeManager.parent_site` - select a different site.
* :meth:`~fluent_pages.models.UrlNodeManager.get_for_path` - find the node for a path.
* :meth:`~fluent_pages.models.UrlNodeManager.best_match_for_path` - find the node starting with

.. tip:: Finding pages by ID

    When :ref:`FLUENT_PAGES_KEY_CHOICES` is set, specific pages can be fetched
    using :func:`Page.objects.get_for_key() <fluent_pages.models.UrlNodeManager.get_for_key>`.


Creating pages
--------------

The tree can hold different page types.
Always create the specific type needed, for example:

.. code-block:: python

    from django.contrib.auth import get_user_model
    from fluent_pages.pagetypes.flatpage.models import FlatPage

    User = get_user_model()
    admin = User.objects.get(active=True, username='admin')

    page = FlatPage.objects.create(
        # Standard fields
        title="Flat test",
        slug="flat-test",
        status=FlatPage.PUBLISHED,
        author=admin,

        # Type specific fields:
        content="This page is created via the API!"
    )

Now the page will appear too:

.. code-block:: python

    >>> from fluent_pages.models import Page
    >>> Page.objects.published()
    <Queryset [<FluentPage: Homepage>, <BlogPage: Blog>, <FluentPage: Contact>, <FlatPage: Flat test>]>

The same approach can be used for other page types.
Review the model API to see which fields can be used:

* :class:`~fluent_pages.pagetypes.flatpage.models.FlatPage` (provide ``content`` and optionally, ``template_name``).
* :class:`~fluent_pages.pagetypes.redirectnode.models.RedirectNode` (provide ``new_url`` and optionally, ``redirect_type``).
* :class:`~fluent_pages.pagetypes.textfile.models.TextFile` (provide ``content`` and optionally, ``content_type``).

Pages with visible HTML content also inherit from :class:`~fluent_pages.models.HtmlPage`,
which makes the ``meta_keywords``, ``meta_description`` and optional ``meta_title`` available too.

Fluent content pages
~~~~~~~~~~~~~~~~~~~~

A similar way can be used for pages with block content.
This uses the django-fluent-contents_ and django-parler_ API's too:

.. code-block:: python

    from django.contrib.auth import get_user_model
    from fluent_pages.pagetypes.fluentpage.models import FluentPage
    from fluent_contents.plugins.textitem.models import TextItem
    from fluent_contents.plugins.oembeditem.models import OEmbedItem

    User = get_user_model()
    admin = User.objects.get(active=True, username='admin')

    page = FluentPage.objects.language('en').create(
        # Standard fields
        title="Fluent test",
        slug="fluent-test",
        status=FluentPage.PUBLISHED,
        author=admin,
    )

    # Create the placeholder
    placeholder = page.create_placeholder('main')

    # Create the content items
    TextItem.objects.create_for_placeholder(placeholder, text="Hello, World!")
    OEmbedItem.objects.create_for_placeholder(placeholder, embed_url="https://vimeo.com/channels/952478/135740366")

    # Adding another language:
    page.create_translation('nl')
    TextItem.objects.create_for_placeholder(placeholder, language_code="nl", text="Hello, World NL!")
    OEmbedItem.objects.create_for_placeholder(placeholder, language_code="nl", embed_url="https://vimeo.com/channels/952478/135740366")


The ``.language('en')`` is not required, as the current language is selected.
However, it's good to be explicit in case your project is multilingual.
When no language code is given to :meth:`~fluent_contents.models.ContentItemManager.create_for_placeholder`,
it uses the current language that the parent object (i.e. the page) has.

.. _django-parler: https://github.com/django-parler/django-parler
.. _django-fluent-contents: https://github.com/django-fluent/django-fluent-contents
