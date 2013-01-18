from django.utils.safestring import mark_safe
from fluent_pages.extensions import PageTypePlugin, page_type_pool
from fluent_pages.pagetypes.flatpage.admin import FlatPageAdmin
from fluent_pages.pagetypes.flatpage.models import FlatPage


@page_type_pool.register
class FlatPagePlugin(PageTypePlugin):
    model = FlatPage
    model_admin = FlatPageAdmin
    sort_priority = 11

    def get_render_template(self, request, flatpage, **kwargs):
        return flatpage.template_name

    def get_context(self, request, page, **kwargs):
        context = super(FlatPagePlugin, self).get_context(request, page, **kwargs)

        # Just like django.contrib.flatpages, mark content as safe:
        page = context['page']
        page.content = mark_safe(page.content)

        return context
