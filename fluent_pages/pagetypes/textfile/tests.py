from fluent_pages.models import UrlNodeManager, UrlNodeQuerySet
from fluent_pages.pagetypes.textfile.models import TextFile
from fluent_pages.tests.utils import AppTestCase


class TextFileTests(AppTestCase):

    def test_default_manager(self):
        """
        Test that the default manager is correct.
        """
        self.assertIsInstance(TextFile._default_manager, UrlNodeManager)
        self.assertIsInstance(TextFile.objects.all(), UrlNodeQuerySet)
