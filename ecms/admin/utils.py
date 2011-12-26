"""
Extra utilities related to the admin
"""
from django.core import urlresolvers
from ecms.models.db import CmsObject


def get_page_admin_url(page):
    """
    Return the admin URL for a page.
    """
    return urlresolvers.reverse('admin:ecms_cmsobject_change', args=(page.id,))


def get_current_edited_page(request):
    """
    Return the ID of the page which is currently edited.
    Returns None if the is no page being edited.
    """
    match = urlresolvers.resolve(request.path_info)
    if match.namespace == 'admin' and match.url_name == 'ecms_cmsobject_change':
        page_id = int(match.args[0])
        return CmsObject.objects.get(pk=page_id)
    return None
