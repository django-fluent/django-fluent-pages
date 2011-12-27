"""
The view to display CMS content.
"""
import re
from fluent_pages.models import CmsObject
from fluent_pages.admin.utils import get_page_admin_url
from django.views.generic import DetailView, RedirectView


class CmsPageView(DetailView):
    """
    The view which displays a CMS page.
    """
    model = CmsObject

    def get_object(self, queryset=None):
        path = self.kwargs.get('path', self.request.path) or ''
        return self.model.objects.get_for_path_or_404(path)

    def get_context_data(self, **kwargs):
        """Return the template context."""
        return self.object.get_template_context()

    def get_template_names(self):
        return [self.object.layout.template_path]

    def post(self, request, *args, **kwargs):
        """Allow POST requests (for forms) to the page."""
        return self.get(request, *args, **kwargs)


class CmsPageAdminRedirect(RedirectView):
    """
    A view which redirects to the admin.
    """
    def get_redirect_url(self, **kwargs):
        path = self.kwargs.get('path', self.request.path) or ''
        try:
            page = CmsObject.objects.get_for_path(path)
            return get_page_admin_url(page)
        except CmsObject.DoesNotExist:
            # Back to page without @admin, display the error there.
            return '/' + re.sub('@[^@]+/?$', '', path)
