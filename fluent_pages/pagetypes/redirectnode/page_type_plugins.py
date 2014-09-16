from django.http import HttpResponseRedirect
from fluent_pages.extensions import PageTypePlugin, page_type_pool
from fluent_pages.pagetypes.redirectnode.admin import RedirectNodeAdmin
from fluent_pages.pagetypes.redirectnode.models import RedirectNode


@page_type_pool.register
class RedirectNodePlugin(PageTypePlugin):
    model = RedirectNode
    model_admin = RedirectNodeAdmin
    default_in_sitemaps = False

    def get_response(self, request, redirectnode, **kwargs):
        response = HttpResponseRedirect(redirectnode.new_url)
        response.status_code = redirectnode.redirect_type
        return response
