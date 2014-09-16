from __future__ import absolute_import
from fluent_pages.extensions import PageTypePlugin
from .admin import FluentContentsPageAdmin


class FluentContentsPagePlugin(PageTypePlugin):
    """
    Base plugin to render a page with content items.
    """
    #: Defines the model to use to store the custom fields.
    #: It must derive from :class:`~fluent_pages.integration.fluent_contents.FluentContentsPage`.
    model = None
    #: Defines the :class:`~django.contrib.admin.ModelAdmin` class to customize the screen.
    #: It should inherit from :class:`~fluent_pages.integration.fluent_contents.FluentContentsPageAdmin`.
    model_admin = FluentContentsPageAdmin

    def get_render_template(self, request, fluentpage, **kwargs):
        """
        Overwritten to automatically pick up the template used in the admin.
        """
        return self.render_template or self.model_admin.placeholder_layout_template
