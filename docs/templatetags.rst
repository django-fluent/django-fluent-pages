.. _templatetags:

The template tags
=================

The template tags provide a way to include a menu, or breadcrumb in the website.
Load the tags using:

.. code-block:: html+django

    {% load fluent_pages_tags %}


The breadcrumb
---------------

The breadcrumb of the current page can be rendered using:

.. code-block:: html+django

    {% render_breadcrumb %}

It's possible to render the breadcrumb using a custom template:

.. code-block:: html+django

    {% render_breadcrumb template="fluent_pages/parts/breadcrumb.html" %}

The breadcrumb template could look like:

.. code-block:: html+django

    {% if breadcrumb %}
    <ul>
    {% for item in breadcrumb %}
      <li{% if forloop.last %} class="last"{% endif %}><a href="{{ item.url }}">{{ item.title }}</a></li>
    {% endfor %}
    </ul>
    {% endif %}


The menu
---------

The menu of the site can be rendered using:

.. code-block:: html+django

    {% render_menu %}

The menu depth and template are configurable:

.. code-block:: html+django

    {% render_menu max_depth=1 template="fluent_pages/parts/menu.html" %}

The menu template could look like:

.. code-block:: html+django

    {% load mptt_tags %}{% if menu_items %}
    <ul>
      {% recursetree menu_items %}{# node is a Page #}
      <li class="{% if node.is_active %}active{% endif %}{% if node.is_last_child %} last{% endif %}">
        <a href="{{ node.url }}">{{ node.title }}</a>
        {% if children %}<ul>{{ children }}</ul>{% endif %}
      </li>{% endrecursetree %}
    </ul>
    {% endif %}


Advanced features
-----------------

Fetching 'site' and 'page' variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The templates receive a ``site`` and ``page`` variable by default.
In case the template is rendered outsite the regular loop, these fields can be fetched:

.. code-block:: html+django

    {% get_fluent_page_vars %}


Locating custom page type views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a custom page type provides additional views, these can be fetched using:

.. code-block:: html+django

    {% load appurl_tags %}

    {% appurl "my_viewname" %}

    {% appurl "my_viewname" arg1 arg2 %}

    {% appurl "my_viewname" kwarg1=value kwargs2=value %}

These tags locate the page in the page tree, and resolve the view URL from there.
