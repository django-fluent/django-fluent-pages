.. _quickstart:

Quick start guide
=================

Installing django-fluent-pages
------------------------------

Make sure you have the base packages installed::

    pip install Django
    pip install django-fluent-pages

This command installs the base dependencies.
As you add more of the :doc:`pagetypes/index`, additional packages may be required.
This is explained in the documentation for each plugin.

.. tip::
    For optional dependency management, it is strongly recommended that you run the application inside a `virtualenv`.

Starting a project
------------------

For a quick way to have everything configured at once, use our template:

.. code-block:: bash

    mkdir example.com
    django-admin.py startproject "myexample" "example.com" -e "py,rst,example,gitignore" --template="https://github.com/edoburu/django-project-template/archive/django-fluent.zip"

And install it's packages:

.. code-block:: bash

    mkvirtualenv example.com
    pip install -r example.com/requirements.txt

Otherwise, continue with the instructions below:


Basic Settings
--------------

In your existing Django project, the following settings need to be added to :file:`settings.py`:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_pages',
        'mptt',
        'parler',
        'polymorphic',
        'polymorphic_tree',

        # And optionally add the desired page types with their dependencies:

        # - flat pages
        'fluent_pages.pagetypes.flatpage',
        'django_wysiwyg',

        # - redirect nodes
        'fluent_pages.pagetypes.redirectnode',
        'any_urlfield',  # optional but recommended
    )

The following applications are used here:

* The main ``fluent_pages`` package that you always need.
* The main dependencies.
* A selection of page type plugins, and their dependencies.

Since some extra page types are used here, make sure their dependencies are installed::

    pip install django-fluent-pages[flatpage,redirectnode]

Afterwards, you can setup the database::

    ./manage.py migrate  # use 'syncdb' for Django 1.6 and below

.. note::

    Each page type is optional. Only the ``fluent_pages`` application is required, allowing to write custom models and plugins.
    Since a layout with the :ref:`flatpage <flatpage>` and :ref:`redirectnode <redirectnode>` page types provides a good introduction, these are added here.

    Each plugin is easily swappable for other implementations, exactly because everything is optional!
    You can use a different page type, or invert new page types with custom fields.
    It makes the CMS configurable in the way that you see fit.


URL configuration
-----------------

The following needs to be added to :file:`urls.py`:

.. code-block:: python

    urlpatterns += patterns('',
        url(r'', include('fluent_pages.urls'))
    )

.. seealso::
    * To add sitemaps support, see the :doc:`sitemaps` documentation about that.
    * Multilingual support may also require changes, see :doc:`multilingual`.



Template structure
------------------

The page output is handled by templates.
When creating large websites, you'll typically have multiple page templates.
That's why it's recommended to have a single base template for all pages.
This can expose the SEO fields that are part of every HTML page.
As starting point, the following structure is recommended::

    templates/
       base.html
       pages/
          base.html
          default.html
          ...

Now, create a :file:`pages/base.html` template:

.. code-block:: html+django

    {% extends "base.html" %}

    {% block full-title %}{% if page.meta_title %}{{ page.meta_title }}{% else %}{{ block.super }}{% endif %}{% endblock %}
    {% block meta-keywords %}{{ page.meta_keywords }}{% endblock %}
    {% block meta-description %}{{ page.meta_description }}{% endblock %}

    {% block extrahead %}{{ block.super }}{% if page.meta_robots %}
        <meta name="robots" content="{{ page.meta_robots }}" />
    {% endif %}{% endblock %}

These blocks should appear in your  :file:`base.html` template off course.

Your site :file:`base.html` template could look something like this:

.. code-block:: html+django

    {% load fluent_pages_tags %}
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="keywords" content="{% block meta-keywords %}{% endblock %}" />
      <meta name="description" content="{% block meta-description %}{% endblock %}" />
      <title>{% block full-head-title %}{% block head-title %}Untitled{% endblock %} | My site{% endblock %}</title>
      {% block extrahead %}{% endblock %}
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

This base template does the following:

* Expose the placeholders for SEO fields.
* Add a main menu using ``{% render_menu %}``
* Add a breadcrumb using ``{% render_breadcrumb %}``

.. tip::
   Whether ``page.title`` should be included is your own decision.
   You can also let clients enter the ``<h1>`` in the WYSIWYG page content,
   and reserve ``page.title`` for menu titles alone.
   This works really well in practise.

Adding page content
-------------------

This package is very flexible when it comes to choosing page content.
There are several page type plugins available:

* :mod:`fluent_pages.pagetypes.flatpage` - a simple page with WYSIWYG text box.
* :mod:`fluent_pages.pagetypes.fluentpage` - a page with flexible content blocks.
* :ref:`other-known-pagetypes`, such as a FAQ index or Blog index page.

The tree can also contain other node types, e.g.:

* :mod:`fluent_pages.pagetypes.redirectnode` - a redirect.
* :mod:`fluent_pages.pagetypes.text` - a plain text file, e.g. to add a `humans.txt <http://humanstxt.org/>`_ file.
* or any :ref:`custom page type <newpagetypes>` you create.

.. seealso::
   In this quick-start manual, we'll discuss the most important options briefly below.
   See the :doc:`pagetypes/index` for the full documentation about each page type.

Using the flatpage plugin
~~~~~~~~~~~~~~~~~~~~~~~~~

The :ref:`Flat page <flatpage>` page type displays a simple WYSIWYG text box.
To use it, install the packages and desired plugins::

    pip install django-fluent-pages[flatpage]
    pip install django-tinymce

.. tip::
   You can also use CKEditor, Redactor or an other WYSIWYG editor,
   but for convenience TinyMCE is used as example.
   See the documentation of the :ref:`flatpage` for details.

Add the following settings:

.. code-block:: python

    INSTALLED_APPS += (
        'fluent_pages.pagetypes.flatpage',
        'django_wysiwyg',
        'tinymce',
    )

    DJANGO_WYSIWYG_FLAVOR = "tinymce"    # or "tinymce_advanced"
    FLUENT_TEXT_CLEAN_HTML = True
    FLUENT_TEXT_SANITIZE_HTML = True

Make sure the database tables are created::

    ./manage.py migrate

To render the output properly, create a :file:`fluent_pages/base.html` file
so the :ref:`Flat page <flatpage>` pages can map the block names to the ones you use in :file:`base.html`:

.. code-block:: html+django

    {% extends "pages/base.html" %}

    {% block head-title %}{% block title %}{% endblock %}{% endblock %}

    {% block main %}{% block content %}{% endblock %}{% endblock %}


Using the fluentpage plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Make sure the database tables are created::

    ./manage.py migrate

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

.. _django-fluent-contents: https://django-fluent-contents.readthedocs.io/en/latest/
.. _django-polymorphic-tree: https://github.com/edoburu/django-polymorphic-tree
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg/
