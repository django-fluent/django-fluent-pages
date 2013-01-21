.. _quickstart:

Quick start guide
=================

Installing django-fluent-pages
------------------------------

The base installation of django-fluent-pages requires Django version 1.3.

The package can be installed using::

    pip install django-fluent-pages

This command only installs the base dependencies (django-polymorphic-tree_).
Any bundled page type may require additional packages, which is explained in the documentation for that page type.
For optional dependency management, it is strongly recommended that you run the application inside a `virtualenv`.


Basic setup
-----------

Next, create a project which uses the module.
The basic module can be installed and optional plugins can be added:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_pages',

        # And optionally add the desired page types:
        'fluent_pages.pagetypes.flatpage',         # requires django-wysiwyg
        'fluent_pages.pagetypes.redirectnode',     # requires django-any-urlfield

        # Dependencies of the page types
        'django_wysiwyg',
        'any_urlfield',
    )

Since some extra page types are used here, make sure their dependencies are installed::

    pip install django-fluent-pages[flatpage,redirectnode]

The reason that all these features are optional is make them easily swappable for other implementations.
You can use a different page type, or invert new page types with custom fields.
It makes the CMS configurable in the way that you see fit.

.. note::

    Each package is optional. Only the ``fluent_pages`` application is required, allowing to write custom models and plugins.
    Since a layout with the :ref:`flatpage <flatpage>` and :ref:`redirectnode <redirectnode>` page types provides a good introduction, these are added here.

Afterwards, you can setup the database::

    ./manage.py syncdb


Displaying flat page content
----------------------------

To render the output properly, create a :file:`fluent_pages/base.html` file so the :ref:`Flat page <flatpage>` pages can map the block names:

.. code-block:: html+django

    {% extends "mysite/base.html" %}

    {% block headtitle %}{% block title %}{% endblock %}{% endblock %}

    {% block main %}{% block content %}{% endblock %}{% endblock %}

Your site base template could look like:

.. code-block:: html+django

    {% load fluent_pages_tags %}
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="keywords" content="{% block meta-keywords %}{% endblock %}" />
      <meta name="description" content="{% block meta-description %}{% endblock %}" />
      <title>{% block headtitle %}{{ page.title }}{% endblock %} - My site</title>
    </head>
    <body>
        <header>
            {% render_menu %}
        </header>

        <section id="contents">
            <div id="main">
                <h1>{{ page.title }}</h1>

                {% render_breadcrumb %}

                {% block main %}{% endblock %}
            </div>
        </section>
    </body>
    </html>


Displaying flexible blocks
--------------------------

The :ref:`Fluent page <fluentpage>` page type can fill parts of the page with flexible content blocks.

To use it, install the packages and desired plugins::

    pip install django-fluent-pages[fluentpage]
    pip install django-fluent-contents[text,code,markup]

Configure the settings:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_pages',
        'fluent_contents',

        # Page types
        'fluent_pages.pagetypes.fluentpage',
        'fluent_pages.pagetypes.flatpage',
        'fluent_pages.pagetypes.redirectnode',

        # Several content plugins
        'fluent_contents.plugins.text',                # requires django-wysiwyg
        'fluent_contents.plugins.code',                # requires pygments
        'fluent_contents.plugins.gist',
        'fluent_contents.plugins.googledocsviewer',
        'fluent_contents.plugins.iframe',
        'fluent_contents.plugins.markup',
        'fluent_contents.plugins.rawhtml',
    )

    FLUENT_MARKUP_LANGUAGE = 'reStructuredText'        # can also be markdown or textile

The template can be filled with the "placeholder" tags from django-fluent-contents_:

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


Testing your new shiny project
------------------------------

Congrats! At this point you should have a working installation.
Now you can just login to your admin site and see what changed.

.. _django-fluent-contents: http://django-fluent-contents.readthedocs.org/en/latest/
.. _django-polymorphic-tree: https://github.com/edoburu/django-polymorphic-tree
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg/
