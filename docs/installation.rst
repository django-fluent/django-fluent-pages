.. _installation:

Full Installation Guide
=======================

.. note::
    Since a CMS is typically the first Django project to install, this installation assumes no existing knowledge of Django.
    For a quick installation guide, see the :doc:`quickstart`.

A brief introduction
--------------------

Django is a web framework to quickly build highly advanced web sites and web applications.
What's striking for some developers, is that Django does not offer a the scenario of "just upload all files".
While seeming odd, this is for a good reason.

It is designed to scale to large web sites.
The key aspects of Django are:

* Django applications are installed "system wide".
  This allows multiple web sites to easily use the same code.
* Django applications have much emphasis on being configurable.
  This makes custom features easily possible with very little time or effort.
* Django applications load once in memory, and stay there.
  The application can execute some static initialisation before loading.
* Django can easily connect to different databases types.
* Django web sites can easily run as separate user accounts, vastly improving security.

There much emphasis on being configurable instead of being a fixed "out of the box" system.
In the long run, this makes adding custom features possible with very little time or effort.
Since you've may never have installed a Python web site before, 
this tutorial is designed to guide you through the whole installation process.

.. note::
    If you're coming from a PHP background, it may seem strange there are more steps then "just upload some files, and edit config.php".
    Please understand there are good reasons for this, see if you can figure out why!

    Also remember, was installing the first web site that easy? Was there nothing to figure out?
    The same applies to Django. After a few times, you just know how the way to do it.


Installing system packages
--------------------------

To install Django packages, the following software needs to be installed at the server:

* Python 2.6
* PIL (Python Image Library)
* pip

In case `pip` is not installed, you can either install it from the package manager (on Linux),
or use the older Python package installer to install it::

    easy_install pip


Setup virtualenv
----------------

Python packages are typically installed system wide. It is much easier however,
to use separate Python environments for each project.
This can be created with `virtualenv`.

A virtualenv (virtual environment) contains a complete Python installation,
separated from the rest of the system. It makes dependency management much easier.
This is an optional step, but highly required one.

First install the following packages:

* ``virtualenv``
* ``virtualenvwrapper``

These packages can either be installed with the package manager (on Linux), or be installed using `pip`::

    pip install virtualenv virtualenvwrapper

Additionally, this code needs to be added to your ``~/.bashrc`` or ``~/.profile`` file:

.. code-block:: sh

    export WORKON_HOME=~/.virtualenvs/
    source /usr/bin/virtualenvwrapper.sh

This also specifies where the virtual environments are stored.
This can be either in your home directory (for local development),
or system wide (for server setups). Feel free to use any location you like.
For your inspiration, typical paths you could use are:

* ``~/bin/virtualenvs/``     (useful for Linux)
* ``~/Sites/virtualenvs/``   (useful for MacOS X)
* ``/srv/www/virtualenvs/``  (system wide, for servers)
* ``/export/virtualenvs/``   (system wide, for servers)

Finally, the environment for this project can be created.
This is done with::

    mkvirtualenv ecms

This creates an separate Python installation folder in ``$WORKON_HOME/ecms``.
Either use the name of your project, or use a shared name in the beginning (like `ecms`).

When you develop from the shell, you need to activate the virtual environment before you start::

    workon ecms

The ``workon`` command changes the ``$PATH``, to make the environment active.
To leave the virtual environment, type::

    deactivate

.. note::
    To completely isolate the environment, you can use the ``--no-site-packages`` argument for ``mkvirtualenv``.
    This makes sure none of the system packages in ``/usr/lib/python2.6/site-packages/`` are available in the environment.
    It also requires you to have a C compiler available, because the MySQL or PostgreSQL packages need it for their installation.

Installing django-ecms
----------------------

Within the virtual environment (or global installation if you skipped the first step),
you can install django-ecms. This is done using::

    cd django-ecms
    python setup.py install

The setup will automatically download Django, and all required packages for a minimal installation.

We'll also be using the `django-admin-tools` package, so install that as well::

    pip install django-admin-tools


Creating a web site project
---------------------------

The django-ecms module can now be used by a Django project.
A Django project works like an empty boiler place.
You can hook all kinds of modules (called applications) in the site, creating the exact setup you need.
This is why every Django application gives instructions on what to add to ``settings.py`` and ``urls.py``.

First, create a project which uses the CMS::

    cd /my/projects/folder/
    django-admin.py startproject mysite

It should have the following settings::

    INSTALLED_APPS += (
        # The CMS apps
        'ecms',
        'ecms_admin_overlay',
        'ecms_dashboard',
        'ecms_media',

        # The CMS content plugins
        'ecms_plugins.text',

        # Support libs
        'mptt',
        'admin_overlay',
        'django_wysiwyg',

        # enable the admin
        'admin_tools',
        'admin_tools.theming',
        'admin_tools.menu',
        'admin_tools.dashboard',
        'django.contrib.admin',
    )

    ADMIN_TOOLS_INDEX_DASHBOARD = 'ecms_dashboard.dashboard.EcmsIndexDashboard'
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'ecms_dashboard.dashboard.EcmsAppIndexDashboard'
    ADMIN_TOOLS_MENU = 'ecms_dashboard.menu.EcmsMenu'

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

Note each CMS application is optional. Only ``ecms`` and ``mptt`` are required.
The remaining apps add additional functionality to the system, such as the custom dashboard or a media browser.
If you want to disable a particular  module, just remove or comment it out in your ``INSTALLED_APPS``.


.. important::
    it is very important that you put the ``admin_tools`` modules **before** 
    the ``django.contrib.admin module``, because it overrides
    the default Django admin templates, and this will not work otherwise.
    The same applies for the ``admin_overlay`` module,
    it needs to be loaded before ``ecms_admin_overlay``.

The following settings are required in ``urls.py``::

    from django.contrib import admin
    admin.autodiscover()

    urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^admin_tools/', include('admin_tools.urls')),
        url(r'', include('ecms.urls'))
    )


Setting up the database
~~~~~~~~~~~~~~~~~~~~~~~

To set up the tables that django-ecms uses you'll need to type::

    ./manage.py syncdb

Initial data can be added, so the CMS opens with a welcome page::

    ./manage.py loaddata welcome


Starting the project
~~~~~~~~~~~~~~~~~~~~

Congrats! At this point you should have a working installation of django-ecms.
To view the web site, you can start the development server::

    ./manage.py runserver

You can open the browser at http://localhost:8000/ to see the first welcome page.
The administrator interface can be accessed at http://localhost:8000/admin/.

django-ecms is fully customizable, but this is out of the scope of this guide.
To learn how to customize django-ecms modules please read
:ref:`the customization section<customization>`.


Optional steps
--------------

Including South
~~~~~~~~~~~~~~~

To go straight for the optimal situation, it is recommended to install `South <http://south.aeracode.org>`_.
This makes it possible to do automatic database upgrades (called migrations) when upgrading packages.

South can be installed like any other Django package. First install it using `pip`::

    pip install south

Next, add it do the ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...

        'south',
    )

Now, the ``manage.py`` command has a few new sub commands available.
For example, database tables can be upgraded using::

    ./manage.py migrate

Because the database tables were created before with ``./manage.py syncdb``, the ``./manage.py migrate`` command
will fail the first time because it tries to recreate the tables again. This can be fixed using::

    ./manage.py migrate --fake

This tells South it needs to skip all existing migrations, because the tables already exist.

A quick overview:

.. code-block:: sh

    ./manage.py migrate              # Do the migration of all packages
    ./manage.py migrate --list       # See all migations available, and which dones are open.
    ./manage.py migrate app          # Migrate a single application
    ./manage.py migrate app --fake   # Tell south that the migrations were already done, so it updates the administration

    ./manage.py migrate app 0003     # Migrate forward (or backward) to a particular migration.

    # And for development:
    ./manage.py conver_to_south app         # Convert an existing application to South.
    ./manage.py startmigration app --auto   # Create the next migration for the model changes.



Connecting to a database server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, Django uses SQLite3 for it's database, which is fine for development.
For production servers, either MySQL or PostgreSQL is recommended.
In ``settings.py``, the database driver and credentials can be entered.

The database driver can be installed using::

    pip install MySQLdb     # MySQLdb driver for MySQL
    pip install psychopg2   # pg2 driver for PostgreSQL


Deploying to Apache
~~~~~~~~~~~~~~~~~~~

The ``runserver`` command provides everything that's needed for local development.
To deploy to the final server, Django offers various solutions.
The recommended solution is using `mod_wsgi` in Apache.

WSGI is the standard solution for hosting Python projects in a web server.
The project needs to provide a ``.wsgi`` file that exports an ``application`` object.
For example, create a ``mysite/deploy/production.wsgi`` file with the following contents::

    import os
    import sys 

    # Detect current path
    file_path   = os.path.realpath(__file__)
    base_folder = os.path.dirname(os.path.dirname(file_path))

    # Set startup settings
    sys.path.append(base_folder)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    sys.stdout = sys.stderr    # redirect print statements to apache log

    # Export application object
    from django.core.handlers.wsgi import WSGIHandler
    application = WSGIHandler()

The static files which ship with all Django modules, need to be collected in a single folder.
Django provides the following command for this::

    ./manage.py collectstatic --link

Now, the WSGI configuration can be added in the Apache web server. An example configuration:

.. code-block:: apache

    <VirtualHost __default__:80>
      ServerName www.example.com

      # Serve static and media files
      Alias /static/ /srv/www/webapps/example.com/mysite/static/
      Alias /media/ /srv/www/webapps/example.com/mysite/media/

      # Configure WSGI application pool in daemon mode
      WSGIDaemonProcess mysite user=wsgiuser group=wsgiusers threads=25 display-name=%{GROUP} python-path=/srv/www/virtualenvs/ecms/lib/python2.6/site-packages
      WSGIScriptAlias "/" /srv/www/webapps/example.com/mysite/deploy/production.wsgi process-group=mysite

      # Permissions
      <Directory "/srv/www/webapps/example.com/mysite/deploy/">
        Order deny,allow
        Allow from all
      </Directory>

      <Directory /srv/www/webapps/example.com/mysite/static/>
        Allow from all
        Order Allow,Deny
        Options +FollowSymlinks
      </Directory>

      <Directory /srv/www/webapps/example.com/mysite/media/>
        Allow from all
        Order Allow,Deny
      </Directory>
    </VirtualHost>

Naturally, the user and group mentioned in the ``WSGIDaemonProcess`` line should be created::

    groupadd -r wsgiusers
    useradd -r -g wsgiusers wsgiuser

It is recommended to run each site with a separate user account, improving the security.

The Apache server needs to be restarted::

    apachectl restart

When using ``ps auxf`` you should see the WSGI container in the process list, started by Apache.
This is where all Django code is loaded.

Eeach time a new version is deployed to the server, the WSGI container needs to be reloaded.
This can be done by touching the ``.wsgi`` file::

    touch -c  /srv/www/webapps/example.com/mysite/deploy/production.wsgi

