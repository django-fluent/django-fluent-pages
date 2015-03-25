from fluent_pages.extensions import page_type_pool
from fluent_pages.integration.fluent_contents.page_type_plugins import FluentContentsPagePlugin
from .models import FluentPage
from .admin import FluentPageAdmin


@page_type_pool.register
class FluentPagePlugin(FluentContentsPagePlugin):
    model = FluentPage
    model_admin = FluentPageAdmin
    sort_priority = 10

    def get_render_template(self, request, fluentpage, **kwargs):
        # Allow subclasses to easily override it by specifying `render_template` after all.
        # The default, is to use the template_path from the layout object.
        return self.render_template or fluentpage.layout.template_path
