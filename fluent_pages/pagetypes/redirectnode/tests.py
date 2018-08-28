from any_urlfield.models import AnyUrlValue
from fluent_pages.models import UrlNodeManager, UrlNodeQuerySet
from fluent_pages.pagetypes.redirectnode.models import RedirectNode
from fluent_pages.tests.testapp.models import SimpleTextPage
from fluent_pages.tests.utils import AppTestCase


class RedirectNodeTests(AppTestCase):

    def test_default_manager(self):
        """
        Test that the default manager is correct.
        """
        self.assertIsInstance(RedirectNode._default_manager, UrlNodeManager)
        self.assertIsInstance(RedirectNode.objects.all(), UrlNodeQuerySet)

    def test_resolve_anyurlfield(self):
        root = SimpleTextPage.objects.create(title="Home", slug="home", status=SimpleTextPage.PUBLISHED, author=self.user, override_url='/')
        RedirectNode.objects.create(
            title="Redirect", status=RedirectNode.PUBLISHED, author=self.user,
            parent=root, slug="redirect", new_url=AnyUrlValue('fluent_pages.urlnode', root.pk))
        response = self.client.get('/redirect/')
        self.assertRedirects(response, '/')
