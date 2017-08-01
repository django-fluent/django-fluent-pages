from fluent_pages.models import UrlNodeManager, UrlNodeQuerySet
from fluent_pages.pagetypes.flatpage.models import FlatPage
from fluent_pages.tests.utils import AppTestCase


class FlatPageTests(AppTestCase):

    def test_default_manager(self):
        """
        Test that the default manager is correct.
        """
        self.assertIsInstance(FlatPage._default_manager, UrlNodeManager)
        self.assertIsInstance(FlatPage.objects.all(), UrlNodeQuerySet)
