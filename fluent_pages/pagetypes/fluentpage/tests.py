import django

from fluent_pages.models import UrlNodeManager, UrlNodeQuerySet
from fluent_pages.pagetypes.fluentpage.models import FluentPage
from fluent_pages.tests.utils import AppTestCase


class FluentPageTests(AppTestCase):

    def test_default_manager(self):
        """
        Test that the default manager is correct.
        """
        if django.VERSION < (1, 10):
            self.assertIsInstance(FluentPage._default_manager, UrlNodeManager)
        self.assertIsInstance(FluentPage.objects.all(), UrlNodeQuerySet)
