from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils.unittest import SkipTest
from fluent_pages.models import Page
from fluent_pages.tests.utils import script_name
from fluent_pages.tests.testapp.models import PlainTextPage


class UrlResolverTests(TestCase):
    """
    Tests for URL resolving.
    """
    root_url = '/'
    subpage1_url = '/test_subpage1/'


    @classmethod
    def setUpClass(cls):
        # When a simplepage is introduced, it can be used instead.
        # For now, rely on the testapp.
        if 'fluent_pages.tests.testapp' not in settings.INSTALLED_APPS:
            raise SkipTest("{0} can only run when 'fluent_pages.tests.testapp' is installed.".format(cls.__name__))

        Site.objects.create(id=settings.SITE_ID, domain='django.localhost', name='django at localhost')
        user, _ = User.objects.get_or_create(is_superuser=True, is_staff=True, username="admin")
        root = PlainTextPage(title="Home", slug="home", status=PlainTextPage.PUBLISHED, author=user, override_url='/')
        root.save()
        subpage1 = PlainTextPage(title="Text1", slug="test_subpage1", status=PlainTextPage.PUBLISHED, author=user)
        subpage1.save()


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
