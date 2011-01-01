"""
A collection of views to display the CMS content
"""
from ecms.models import CmsObject
from django.template.context import RequestContext
from django.shortcuts import render_to_response


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

    # Render the page
    context = page.get_template_context()
    return render_to_response("ecms/cmspage.html", context, context_instance=RequestContext(request))
