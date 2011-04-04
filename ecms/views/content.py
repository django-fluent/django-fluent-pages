"""
A collection of views to display the CMS content
"""
from ecms.models import CmsObject
from django.template.context import RequestContext
from django.http import HttpResponse


def cmspage(request, path):
    """
    Display a CMS page.
    """
    if path is None:
        path = request.path

    # Get current page,
    page = CmsObject.objects.get_for_path_or_404(path)

    # allow template tags to track the current page.
    request._ecms_current_page = page

    # Render it
    # Logic for rendering is stored in the layout
    context = page.get_template_context()
    template = page.layout.get_template()
    html = template.render(RequestContext(request, context))
    return HttpResponse(html)
