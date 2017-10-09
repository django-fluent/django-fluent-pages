from __future__ import absolute_import

from django.contrib import admin

from fluent_pages.extensions import PageTypePlugin

from .admin import FluentContentsPageAdmin


class FluentContentsPagePlugin(PageTypePlugin):
    """
    Base plugin to render a page with content items.
    """
    #: Defines the model to use to store the custom fields.
    #: It must derive from :class:`~fluent_pages.integration.fluent_contents.FluentContentsPage`.
    model = None

    #: Defines the default :class:`~django.contrib.admin.ModelAdmin` class for the add/edit screen.
    #: It should inherit from :class:`~fluent_pages.integration.fluent_contents.FluentContentsPageAdmin`.
    model_admin = FluentContentsPageAdmin

    def get_render_template(self, request, fluentpage, **kwargs):
        """
        Overwritten to automatically pick up the template used in the admin.
        """
        if self.render_template:
            return self.render_template

        try:
            # Try using the actual admin registered,
            # not what the plugin promises.
            model_admin = admin.site._registry[self.model]
        except KeyError:
            # Fallback to the old model_admin attribute
            model_admin = self.model_admin

        # When the model admin isn't a FluentContentsPageAdmin,
        # return None just as if the attribute was not filled in.
        return getattr(model_admin, 'placeholder_layout_template', None)
