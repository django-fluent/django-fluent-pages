.. _dependencies:

Package dependencies
====================

This is a quick overview of all used Django packages:

.. graphviz::

    digraph G {
        fontname = "Bitstream Vera Sans"
        fontsize = 8

        node [
            fontname = "Bitstream Vera Sans"
            fontsize = 8
            shape = "record"
            style = "filled"
            fillcolor = "gray80"
        ]

        edge [
            fontname = "Bitstream Vera Sans"
            fontsize = 8
        ]

        subgraph clusterFluentPages {
            label = "This package"

            fluent_pages [
                label = "django-fluent-pages"
            ]

            subgraph clusterPagetypes {
                label = "fluent_pages.pagetypes"

                fluentpage [
                    label = "fluentpage"
                ]

                flatpage [
                    label = "flatpage"
                ]

                redirectnode [
                    label = "redirectnode"
                ]

                textfile [
                    label = "textfile"
                ]
            }
        }

        any_urlfield [
            label = "django-any-urlfield"
        ]

        django_wysiwyg [
            label = "django-wysiwyg"
        ]

        fluent_contents [
            label = "django-fluent-contents"
        ]

        django_polymorphic [
            label = "django-polymorphic"
        ]

        django_mptt [
            label = "django-mptt"
        ]

        django_polymorphic_tree [
            label = "django-polymorphic-tree"
        ]

        fluentpage -> fluent_contents
        flatpage -> django_wysiwyg
        redirectnode -> any_urlfield [style=dashed]

        fluent_pages -> django_polymorphic_tree [lhead=clusterFluentPages]
        django_polymorphic_tree -> django_polymorphic
        django_polymorphic_tree -> django_mptt
    }

The used packages are:

.. glossary::

    django-any-urlfield_:

        An URL field which can also point to an internal Django model.

    django-fluent-contents_:

        The widget engine for flexible block positions.

    django-mptt_:

        The structure to store tree data in the database.

        Note that *django-fluent-pages* doesn't
        use a 100% pure MPTT tree, as it also stores a ``parent_id`` and ``_cached_url`` field in the database.
        These fields are added for performance reasons, to quickly resolve parents, children and pages by URL.

    django-polymorphic_:

        Polymorphic inheritance for Django models, it lets queries return the derived models by default.

    django-polymorphic-tree_

        The tree logic, where each node can be a different model type.

    django-wysiwyg_:

        A flexible WYSIWYG field, which supports various editors.


.. _django-any-urlfield: https://github.com/edoburu/django-any-urlfield
.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
.. _django-mptt: https://github.com/django-mptt/django-mptt
.. _django-polymorphic: https://github.com/chrisglass/django_polymorphic
.. _django-polymorphic-tree: https://github.com/edoburu/django-polymorphic-tree
.. _django-wysiwyg: https://github.com/pydanny/django-wysiwyg
