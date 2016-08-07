Management Commands
===================

The following management commands are provided for administrative utilities:


make_language_redirects
-----------------------

When a language is unmaintained at the site,
use this command to generate the URL redirects.
The command outputs a script for the web server (currently only in Nginx format).

Options:

* :samp:`--from={language}`: the old language
* :samp:`--to={language}`: the new language
* :samp:`--format={nginx}`: the format
* :samp:`--site={id}`: the site for which redirects are created.

Example:

.. code-block:: bash

    python manage.py make_language_redirects --from=it --to=en --format=nginx --site=1


rebuild_page_tree
-----------------

In the unlikely event that the page tree is broken, this utility repairs the tree.
This happened in earlier releases (before 1.0) when entire trees were moved in multi-lingual sites.

It regenerates the MPTT fields and URLs.

Options:

* ``-p`` / ``--dry-run``: tell what would happen, but don't make any changes.
* ``-m`` / ``--mptt-only``: only regenerate the MPTT fields, not the URLs of the tree.

Example:

.. code-block:: bash

    python manage.py rebuild_page_tree


prefix_pagetypes
----------------

This adds prefixes to the ``ContentType`` names in the database,
to easily recognize the custom page types.
This happens by default during migrations.

.. code-block:: bash

    python manage.py prefix_pagetypes
