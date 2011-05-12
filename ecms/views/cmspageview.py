"""
The view to display CMS content.
"""
from ecms.models import CmsObject
from django.views.generic import DetailView


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
