"""
Tests for the ECMS code
"""
from contextlib import contextmanager
from django.conf import settings
from django.core.urlresolvers import get_script_prefix, set_script_prefix
from django.test import TestCase
from fluent_pages.models.db import Page

@contextmanager
def script_name(newpath):
    """
    Simulate that the application has a different root folder, expressed by the ``SCRIPT_NAME`` variable.
    This can happen for example, by using ``WSGIScriptAlias /subfolder`` for the Django site.
    It causes ``request.path`` and ``request.path_info`` to differ, making it important to use the right one.
    """
    if newpath[0] != '/' or newpath[-1] != '/':
        raise ValueError("Path needs to have slashes at both ends.")

    newpath_noslash = newpath.rstrip('/')
    oldprefix = get_script_prefix()
    oldname = settings.FORCE_SCRIPT_NAME
    oldmedia = settings.MEDIA_URL
    oldstatic = settings.STATIC_URL

    # Auto adjust MEDIA_URL if it's not set already.
    if settings.MEDIA_URL[0] == '/' and not settings.MEDIA_URL.startswith(newpath):
        settings.MEDIA_URL = newpath_noslash + settings.MEDIA_URL
    if settings.STATIC_URL[0] == '/' and not settings.STATIC_URL.startswith(newpath):
        settings.STATIC_URL = newpath_noslash + settings.STATIC_URL

    settings.FORCE_SCRIPT_NAME = newpath
    set_script_prefix(newpath)
    try:
        yield  # call code inside 'with'
    finally:
        settings.FORCE_SCRIPT_NAME = newpath_noslash
        settings.STATIC_URL = oldstatic
        settings.MEDIA_URL = oldmedia
        set_script_prefix(oldprefix)


class EcmsUrlTests(TestCase):
    """
    Tests for URL resolving.
    """
    fixtures = ['testdata']
    root_url = '/'
    subpage1_url = '/test_subpage1/'


    def test_get_for_path(self):
        # TODO: apply reverse() to support different URLconf layouts.
        subpage = Page.objects.get_for_path(self.subpage1_url)
        self.assertIsNotNone(subpage)
        self.assertEquals(subpage.get_absolute_url(), self.subpage1_url, "Page at {0} has invalid absolute URL".format(self.subpage1_url))
        self.assertEquals(self.client.get(self.root_url).status_code, 200, "Page at {0} should be found.".format(self.root_url))
        self.assertEquals(self.client.get(self.subpage1_url).status_code, 200, "Page at {0} should be found.".format(self.subpage1_url))

    def test_get_for_path_script_name(self):
        with script_name('/_test_subdir_/'):
            subpage = Page.objects.get_for_path(self.subpage1_url)
            self.assertIsNotNone(subpage)
            self.assertEquals(subpage.get_absolute_url(), '/_test_subdir_' + self.subpage1_url, "CmsObject.get_absolute_url() should take changes to SCRIPT_NAME into account (got: {0}).".format(subpage.get_absolute_url()))
            self.assertEquals(self.client.get(self.root_url).status_code, 200, "Page at {0} should be found.".format(self.root_url))
            self.assertEquals(self.client.get(self.subpage1_url).status_code, 200, "Page at {0} should be found.".format(self.subpage1_url))
