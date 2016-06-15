.. _fluentpage:

The fluentpage page type
========================

The *fluentpage* provides a page type where parts of the page can be filled with flexible content blocks.

  .. image:: /images/pagetypes/fluentpage-admin.*
     :width: 756px
     :height: 726px

This feature is provided by django-fluent-contents_.

The combination of *django-fluent-pages* and *django-fluent-contents* provides the most flexible page layout.
It's possible to use a mix of standard plugins (e.g. *text*, *code*, *forms*) and
customly defined plugins to facilitate complex website designs.
See the documentation of django-fluent-contents_ for more details.


Installation
------------

Install the dependencies via *pip*::

    pip install django-fluent-pages[fluentpage]
    pip install django-fluent-contents[text]

This installs the django-fluent-contents_ package.

Add the following settings to ``settings.py``:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_pages.pagetypes.fluentpage',
        'fluent_contents',

        # The desired plugins for django-fluent-contents, e.g:
        'fluent_contents.plugins.text',
        'django_wysiwyg',
    )


Template design
---------------

To render the page, include the tags that django-fluent-contents_ uses to define placeholders.
For example:

.. code-block:: html+django

    {% extends "mysite/base.html" %}
    {% load placeholder_tags %}

    {% block main %}
        <section id="main">
            <article>
                {% block pagetitle %}<h1 class="pagetitle">{{ page.title }}</h1>{% endblock %}
                {% page_placeholder "main" role='m' %}
            </article>

            <aside>
                {% page_placeholder "sidebar" role='s' %}
            </aside>
        </section>
    {% endblock %}

These placeholders will be detected and displayed in the admin pages.

Place the template in the template folder that :ref:`FLUENT_PAGES_TEMPLATE_DIR` points to.
By default, that is the first path in ``TEMPLATE_DIRS``.


Configuration
-------------

The page type itself doesn't provide any configuration options,
everything can be fully configured by configuring django-fluent-contents_.
See the documentation of each of these :ref:`bundled content plugins <fluentcontents:bundled-content-plugins>` to use them:

* :ref:`fluentcontents:code`
* :ref:`fluentcontents:commentsarea`
* :ref:`fluentcontents:disquscommentsarea`
* :ref:`fluentcontents:formdesignerlink`
* :ref:`fluentcontents:gist`
* :ref:`fluentcontents:googledocsviewer`
* :ref:`fluentcontents:iframe`
* :ref:`fluentcontents:markup`
* :ref:`fluentcontents:oembeditem`
* :ref:`fluentcontents:rawhtml`
* :ref:`fluentcontents:sharedcontent`
* :ref:`fluentcontents:text`
* :ref:`fluentcontents:twitterfeed`


Creating new plugins
~~~~~~~~~~~~~~~~~~~~

A website with custom design elements can be easily editable by creating custom plugins.

Creating new plugins is not complicated at all, and simple plugins can can easily be created within 15 minutes.

The documentation of django-fluent-contents_ explains :ref:`how to create new plugins <fluentcontents:newplugins>` in depth.


Advanced features
-----------------

This module also provides the :class:`~fluent_pages.pagetypes.fluentpage.models.FluentPageBase`
and :class:`~fluent_pages.pagetypes.fluentpage.admin.FluentPageAdmin` classes,
which can be used as base classes for :ref:`custom page types <newpagetypes>`
that also use the same layout mechanisms.


.. _django-fluent-contents: https://django-fluent-contents.readthedocs.io/en/latest/
