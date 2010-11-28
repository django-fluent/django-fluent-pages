"""
A collection of views to display the CMS content
"""
from django.http import HttpResponse
from ecms.models import CmsSite, CmsObject
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.utils.functional import LazyObject, SimpleLazyObject


def cmspage(request, path):
    """
    Display a CMS page.
    """
    if path is None:
        path = request.path

    # Get current page,
    # allow template tags to track the current page.
    site = CmsSite.objects.get_current(request)
    page = CmsObject.objects.get_for_path_or_404(path)
    request._ecms_current_page = page

    # Render the template
    context = {
        'ecms_site': site,
        'ecms_page': page,
    }

    return render_to_response("ecms/cmspage.html", context, context_instance=RequestContext(request))
