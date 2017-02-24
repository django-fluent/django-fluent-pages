from fluent_pages.integration.fluent_contents import FluentContentsPage
from fluent_pages.models import UrlNodeManager
from fluent_pages.tests.utils import AppTestCase


class FluentContentsPageTests(AppTestCase):

    def test_default_manager(self):
        """
        Test that the default manager is correct.
        """
        self.assertIsInstance(FluentContentsPage._default_manager, UrlNodeManager)

        class ExamplePage(FluentContentsPage):
            pass

        self.assertIsInstance(ExamplePage._default_manager, UrlNodeManager)
