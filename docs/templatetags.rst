.. _templatetags:

The template tags
=================

The template tags provide a way to include a menu, or breadcrumb in the website.
Load the tags using:

.. code-block:: html+django

    {% load fluent_pages_tags %}


The breadcrumb
--------------

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
--------

The menu of the site can be rendered using:

.. code-block:: html+django

    {% render_menu %}

The number of levels can be limited using the ``depth`` parameter:

.. code-block:: html+django

    {% render_menu depth=1 %}

Custom menu template
~~~~~~~~~~~~~~~~~~~~

The template parameter offers a way to define your own menu layout. For example:

.. code-block:: html+django

    {% render_menu max_depth=1 template="fluent_pages/parts/menu.html" %}

The menu template could look like:

.. code-block:: html+django

    {% load mptt_tags %}
    {% if menu_items %}
      <ul>
        {% recursetree menu_items %}
        <li class="{% if node.is_active or node.is_child_active %}active{% endif %}{% if node.is_draft %} draft{% endif %}">
          <a href="{{ node.url }}">{{ node.title }}</a>
          {% if children %}<ul>{{ children }}</ul>{% endif %}
        </li>{% endrecursetree %}
      </ul>
    {% else %}
      <!-- Menu is empty -->
    {% endif %}

The ``node`` variable is exposed by the ``{% recursetree %}`` tag.
It's a :class:`~fluent_pages.models.navigation.PageNavigationNode` object.

To use a different template, either override the ``fluent_pages/parts/menu.html`` template in your project,
or use the ``template`` variable (recommended). For example, for a Bootstrap 3 project, you can use the following template:

.. code-block:: html+django

    {% load mptt_tags %}
    {% if menu_items %}
    <ul class="nav navbar-nav">
      {% recursetree menu_items %}
      <li class="{% if node.is_active or node.is_child_active %}active{% endif %}">
        {% if children %}
          <a href="{{ node.url }}" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">{{ node.title }} <span class="caret"></span></a>
          <ul class="dropdown-menu" role="menu">{{ children }}</ul>
        {% else %}
          <a href="{{ node.url }}">{{ node.title }}</a>
        {% endif %}
      </li>{% endrecursetree %}
    </ul>
    {% else %}
      <!-- Menu is empty -->
    {% endif %}


Rendering side menu's
~~~~~~~~~~~~~~~~~~~~~

You can render a subsection of the menu using use the ``parent`` keyword argument.
It expects a page object, URL path or page ID of the page you want to start at.
Combined with the ``template`` argument, this gives

.. code-block:: html+django

    {% render_menu parent=page max_depth=1 template="partials/side_menu.html" %}
    {% render_menu parent='/documentation/' max_depth=1 %}
    {% render_menu parent=8 max_depth=1 %}


Advanced features
-----------------

Fetching 'site' and 'page' variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The templates receive a ``site`` and ``page`` variable by default.
In case the template is rendered outside the regular loop, these fields can be fetched:

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
