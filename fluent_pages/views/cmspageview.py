"""
The view to display CMS content.
"""
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.views.generic.base import View
import re
from fluent_pages.models import UrlNode
from fluent_pages.admin.utils import get_page_admin_url
from fluent_pages.extensions import page_type_pool
from django.views.generic import RedirectView


class CmsPageView(View):
    """
    The view which displays a CMS page.
    This is not a ``DetailsView`` by design, as the rendering is redirected to the page type plugin.
    """
    model = UrlNode

    def get(self, request, **kwargs):
        """Display the page in a GET request."""
        path = self.get_path()
        try:
            self.object = self.get_object()
        except Http404:
            # urlconf allows paths to have no trailing slash so it's a catch-all for filenames too.
            # When the actual page exists with a slash, restore the APPEND_SLASH behaviour.
            if path.endswith('/'):
                raise
            self.object = self.get_object(path + '/')
            if settings.APPEND_SLASH:
                return HttpResponseRedirect(path + '/')

        self.plugin = self.get_plugin()
        return self.plugin.get_response(self.request, self.object)

    def post(self, request, **kwargs):
        """Allow POST requests (for forms) to the page."""
        return self.get(request, **kwargs)

    def get_path(self):
        return self.kwargs.get('path', self.request.path) or ''

    def get_object(self, path=None):
        """Return the UrlNode subclass object of the current page."""
        path = path or self.get_path()
        return self.model.objects.get_for_path_or_404(path)

    def get_plugin(self):
        """Return the rendering plugin for the current page object."""
        return page_type_pool.get_plugin_by_model(self.object.__class__)


class CmsPageAdminRedirect(RedirectView):
    """
    A view which redirects to the admin.
    """
    def get_redirect_url(self, **kwargs):
        path = self.kwargs.get('path', self.request.path) or ''
        try:
            page = UrlNode.objects.non_polymorphic().get_for_path(path)
            return get_page_admin_url(page)
        except UrlNode.DoesNotExist:
            # Back to page without @admin, display the error there.
            return '/' + re.sub('@[^@]+/?$', '', path)
