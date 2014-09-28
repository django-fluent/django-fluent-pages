"""
Utility functions related to admin views.
"""
from future.builtins import int
from django.core import urlresolvers
from fluent_pages.models import UrlNode


def get_page_admin_url(page):
    """
    Return the admin URL for a page.
    """
    return urlresolvers.reverse('admin:fluent_pages_page_change', args=(page.pk,))


def get_current_edited_page(request):
    """
    Return the :class:`~fluent_pages.models.Page` object which is currently being edited in the admin.
    Returns ``None`` if the current view isn't the "change view" of the the :class:`~fluent_pages.models.Page` model.
    """
    match = urlresolvers.resolve(request.path_info)
    if match.namespace == 'admin' and match.url_name == 'fluent_pages_page_change':
        page_id = int(match.args[0])
        return UrlNode.objects.get(pk=page_id)
    return None
