from fluent_pages.models import UrlNodeManager, UrlNodeQuerySet
from fluent_pages.pagetypes.redirectnode.models import RedirectNode
from fluent_pages.tests.utils import AppTestCase


class RedirectNodeTests(AppTestCase):

    def test_default_manager(self):
        """
        Test that the default manager is correct.
        """
        self.assertIsInstance(RedirectNode._default_manager, UrlNodeManager)
        self.assertIsInstance(RedirectNode.objects.all(), UrlNodeQuerySet)
