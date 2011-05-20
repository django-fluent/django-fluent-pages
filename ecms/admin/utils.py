"""
Extra utilities related to the admin
"""
from django.core import urlresolvers


def get_page_admin_url(page):
    """
    Return the admin URL for a page.
    """
    return urlresolvers.reverse('admin:ecms_cmsobject_change', args=(page.id,))
