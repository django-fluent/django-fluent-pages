from fluent_pages.tests.testapp.models import WebShopPage
from fluent_pages.tests.utils import AppTestCase


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
        self.assertEquals(WebShopPagePlugin.urls, 'fluent_pages.tests.testapp.urls_webshop')

        # See if the page points to the proper URL resolver
        shop = WebShopPage.objects.all()[0]
        resolver = shop.plugin.get_url_resolver()
        self.assertIsNotNone(resolver, "App pages should have an URL resolver")

        # See if the URL resolver returns the proper functions
        match = resolver.resolve('/')
        self.assertEqual(match.func, webshop_index)

    # TODO: test more stuff.
    # e.g. registration API, supported fields, expected available API functions
