from fluent_pages.tests.testapp.models import WebShopPage
from fluent_pages.tests.utils import AppTestCase
from fluent_pages.urlresolvers import app_reverse, mixed_reverse, PageTypeNotMounted, MultipleReverseMatch


class PluginTests(AppTestCase):
    """
    Test cases for plugins
    """

    @classmethod
    def setUpTree(cls):
        WebShopPage.objects.create(title="Shop1", slug="shop", status=WebShopPage.PUBLISHED, author=cls.user)

    def test_app_page_urlconf(self):
        """
        App pages should have an URL resolver, that returns the custom views.
        """
        from fluent_pages.tests.testapp.page_type_plugins import WebShopPagePlugin
        from fluent_pages.tests.testapp.urls_webshop import webshop_index
        self.assertEqual(WebShopPagePlugin.urls, 'fluent_pages.tests.testapp.urls_webshop')

        # See if the page points to the proper URL resolver
        shop = WebShopPage.objects.all()[0]
        resolver = shop.plugin.get_url_resolver()
        self.assertIsNotNone(resolver, "App pages should have an URL resolver")

        # See if the URL resolver returns the proper functions
        match = resolver.resolve('/')
        self.assertEqual(match.func, webshop_index)

    # TODO: test more stuff.
    # e.g. registration API, supported fields, expected available API functions

    def test_app_reverse(self):
        """
        The app_reverse function should find the proper CMS page where the app is mounted.
        """
        self.assertEqual(WebShopPage.objects.published().count(), 1)

        self.assertEqual(app_reverse('webshop_index'), '/shop/')
        self.assertEqual(app_reverse('webshop_article', kwargs={'slug': 'foobar'}), '/shop/foobar/')

        self.assertEqual(mixed_reverse('webshop_index'), '/shop/')
        self.assertEqual(mixed_reverse('webshop_article', kwargs={'slug': 'foobar'}), '/shop/foobar/')

    def test_app_reverse_multiple(self):
        """
        The app_reverse functions should support multiple mount points for an app.
        """
        shop2 = WebShopPage.objects.create(title="Shop2", slug="shop2", status=WebShopPage.PUBLISHED, author=self.user)
        self.assertEqual(WebShopPage.objects.published().count(), 2)

        # There are now 2 mount points, the functions should detect that
        self.assertRaises(MultipleReverseMatch, lambda: app_reverse('webshop_index'))
        self.assertRaises(MultipleReverseMatch, lambda: mixed_reverse('webshop_index'))

        # The functions have a 'current_page' parameter that allows relative resolving.
        # This is designed for template functions, to allow resolving relative to the current page node.
        self.assertEqual(app_reverse('webshop_index', current_page=shop2), '/shop2/')
        self.assertEqual(app_reverse('webshop_article', current_page=shop2, kwargs={'slug': 'foobar'}), '/shop2/foobar/')

        self.assertEqual(mixed_reverse('webshop_index', current_page=shop2), '/shop2/')
        self.assertEqual(mixed_reverse('webshop_article', current_page=shop2, kwargs={'slug': 'foobar'}), '/shop2/foobar/')

    def test_app_reverse_multiple_language(self):
        """
        The app_reverse functions should skip pages that are not translated in the current language.
        """
        # Recreate models for clarity
        for page in WebShopPage.objects.all():
            page.delete()  # Allow signals to be sent, and clear caches

        WebShopPage.objects.language('en').create(title="Shop3-en", slug="shop3-en", status=WebShopPage.PUBLISHED, author=self.user)
        WebShopPage.objects.language('fr').create(title="Shop4-fr", slug="shop4-fr", status=WebShopPage.PUBLISHED, author=self.user)
        self.assertEqual(WebShopPage.objects.published().count(), 2)

        # Depending on the language, multiple objects can be found.
        # This tests whether _get_pages_of_type() properly filters the language.
        self.assertEqual(app_reverse('webshop_index', language_code='en'), '/shop3-en/')
        self.assertRaises(MultipleReverseMatch, lambda: app_reverse('webshop_index', language_code='fr'))

    def test_app_reverse_unmounted(self):
        """
        The app_reverse functions should raise an exception when the pagetype is not added in the page tree.
        """
        for page in WebShopPage.objects.all():
            page.delete()  # Allow signals to be sent, and clear caches
        self.assertEqual(WebShopPage.objects.published().count(), 0)
        self.assertRaises(PageTypeNotMounted, lambda: app_reverse('webshop_index'))
        self.assertRaises(PageTypeNotMounted, lambda: mixed_reverse('webshop_index'))


class PluginUrlTests(AppTestCase):
    """
    Test for running a pagetype app standalone.
    (some apps will support that, e.g. django-fluent-blogs)
    """
    urls = 'fluent_pages.tests.testapp.urls_webshop'

    def test_mixed_reverse_standalone(self):
        """
        When a custom app is not hooked via the CMS page tree, mixed_reverse() should still work.
        """
        self.assertRaises(PageTypeNotMounted, lambda: app_reverse('webshop_index'))
        self.assertEqual(mixed_reverse('webshop_index'), '/')
        self.assertEqual(mixed_reverse('webshop_article', kwargs={'slug': 'foobar'}), '/foobar/')
