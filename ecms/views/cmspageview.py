"""
The view to display CMS content.
"""
import re
from django.core import urlresolvers
from ecms.models import CmsObject
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


class CmsPageAdminRedirect(RedirectView):
    """
    A view which redirects to the admin.
    """
    def get_redirect_url(self, **kwargs):
        path = self.kwargs.get('path', self.request.path) or ''
        try:
            page = CmsObject.objects.get_for_path(path)
            return urlresolvers.reverse('admin:ecms_cmsobject_change', args=(page.id,))
        except CmsObject.DoesNotExist:
            # Back to page without @admin, display the error there.
            return '/' + re.sub('@[^@]+/?$', '', path)
