Using the example
=================

To run the example application, make sure you have the required packages installed.
You can do this using:

.. code-block:: shell

    mkvirtualenv fpdemo
    pip install -r requirements.txt

(This assumes you already have *virtualenv* and *virtualenvwrapper* installed).

Next, you can setup the Django instance using:

.. code-block:: shell

    ./manage.py syncdb --migrate --noinput
    ./manage.py createsuperuser --username=admin --email=admin@example.com
    ./manage.py loaddata welcome shop_example

And run it off course:

.. code-block:: shell

    ./manage.py runserver

Good luck!

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea, please let us know as well
at https://github.com/edoburu/django-fluent-pages/ because we will look at it.
Pull requests are welcome too. :-)

