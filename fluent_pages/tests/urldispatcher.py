from django.core.urlresolvers import reverse, resolve
try: # django > 1.5
    from django.contrib.auth import get_user_model
    User = get_user_model()
except: # django 1.4
    from django.contrib.auth.models import User
from fluent_pages.models import Page, UrlNode
from fluent_pages.tests.utils import AppTestCase, script_name, override_settings
from fluent_pages.tests.testapp.models import SimpleTextPage, PlainTextFile, WebShopPage
from fluent_pages.views.dispatcher import _try_languages, _get_fallback_language

class UrlDispatcherTests(AppTestCase):
    """
    Tests for URL resolving.
    """

    @classmethod
    def setUpTree(cls):
        User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        SimpleTextPage.objects.create(title="Home", slug="home", status=SimpleTextPage.PUBLISHED, author=cls.user, override_url='/')
        SimpleTextPage.objects.create(title="Text1", slug="sibling1", status=SimpleTextPage.PUBLISHED, author=cls.user, contents="TEST_CONTENTS")
        SimpleTextPage.objects.create(title="Text1", slug="unpublished", status=SimpleTextPage.DRAFT, author=cls.user)
        WebShopPage.objects.create(title="Shop1", slug="shop", status=SimpleTextPage.PUBLISHED, author=cls.user)
        PlainTextFile.objects.create(slug='README', status=PlainTextFile.PUBLISHED, author=cls.user, content="This is the README")
        SimpleTextPage.objects.create(title="Text1", slug="sibling2", status=SimpleTextPage.PUBLISHED, author=cls.user, contents="TEST_CONTENTS", login_required=True)
        WebShopPage.objects.create(title="Shop2", slug="shop2", status=SimpleTextPage.PUBLISHED, author=cls.user, login_required=True)


    def test_get_for_path(self):
        """
        The testdata should be found under the expected URLs.
        """
        # Test basic state
        sibling1 = Page.objects.get_for_path('/sibling1/')
        self.assertEquals(sibling1.get_absolute_url(), '/sibling1/', "Page at {0} has invalid absolute URL".format('/sibling1/'))
        self.assert200('/')
        self.assert200('/sibling1/')

        # Test exceptions
        self.assertRaises(SimpleTextPage.DoesNotExist, lambda: SimpleTextPage.objects.get_for_path('/not-found/'))


    def test_get_append_slash_redirect(self):
        """
        The dispatcher should implement APPEND_SLASH handling,
        because ``fluent_pages.urls`` is a catch-all for ALL url's, including those without a slash.
        """
        with override_settings(APPEND_SLASH=True):
            self.assertRedirects(self.client.get('/sibling1'), '/sibling1/', status_code=302)

        with override_settings(APPEND_SLASH=False):
            self.assert404('/sibling1', 'APPEND_SLASH=False: ')

        # However, non existing pages should not get an APPEND_SLASH redirect
        self.assert404('/not-found')


    def test_hide_unpublished(self):
        """
        Unpublished pages should not appear
        """
        self.assertTrue(SimpleTextPage.objects.filter(translations__slug='unpublished').exists(), "page /unpublished/ should exist in the database.")
        self.assert404('/unpublished/')
        self.assert404('/unpublished')   # With default APPEND_SLASH=True


    def test_get_for_path_script_name(self):
        """
        The dispatcher should support a different WSGIScriptAlias prefix.
        """
        with script_name('/_test_subdir_/'):
            sibling1 = Page.objects.get_for_path('/sibling1/')
            self.assertEquals(sibling1.get_absolute_url(), '/_test_subdir_/sibling1/', "UrlNode.get_absolute_url() should take changes to SCRIPT_NAME into account (got: {0}).".format(sibling1.get_absolute_url()))
            # Note the test client always operates relative to the Django script_name root.
            self.assert200('/')
            self.assert200('/sibling1/')


    def test_page_output(self):
        """
        Pages should render output via the ``render_template``.
        """
        # Test initial state
        from fluent_pages.tests.testapp.page_type_plugins import SimpleTextPagePlugin  # Import here as it needs an existing DB
        self.assertEquals(SimpleTextPagePlugin.render_template, 'testapp/simpletextpage.html')

        # Test how a normal page is rendered
        response = self.client.get('/sibling1/')
        self.assertTemplateUsed(response, 'testapp/simpletextpage.html')
        self.assertContains(response, '<div id="test_contents">TEST_CONTENTS</div>')


    def test_app_page_output(self):
        """
        The resolver should detect that the plugin has an URLconf that overlays the CMS page index url.
        """
        # Test initial state
        from fluent_pages.tests.testapp.page_type_plugins import WebShopPagePlugin
        self.assertEquals(WebShopPagePlugin.urls, 'fluent_pages.tests.testapp.urls_webshop')

        response = self.client.get('/shop/')
        self.assertContains(response, 'test_webshop: index_page')  # The URLconf is an overlay over the standard get_response()


    def test_app_page_url(self):
        """
        The URL that is a mix of DB page + URLconf should match and return.
        """
        response = self.client.get('/shop/foobar/')
        self.assertContains(response, 'test_webshop: article: foobar')


    def test_app_page_unicode_url(self):
        """
        The URL that is a mix
        """
        response = self.client.get(u'/shop/\u20ac/')
        self.assertContains(response, u'test_webshop: article: \u20ac')


    def test_app_page_append_slash(self):
        """
        The APPEND_SLASH setting should also work for app page URLs
        """
        with override_settings(APPEND_SLASH=True):
            self.assertRedirects(self.client.get('/shop'), '/shop/', status_code=302)
            self.assertRedirects(self.client.get('/shop/article1'), '/shop/article1/', status_code=302)

        with override_settings(APPEND_SLASH=False):
            self.assert404('/shop', 'APPEND_SLASH=False')
            self.assert404('/shop/article1', 'APPEND_SLASH=False')

        # However, non resolvable app pages should not get an APPEND_SLASH redirect
        self.assert404('/shop/article1/foo')


    def test_plain_text_file(self):
        """
        URLs that point to files should return properly.
        """
        response = self.client.get('/README')
        self.assertEqual(response.content, 'This is the README')
        self.assertEqual(response['Content-Type'], 'text/plain')


    def test_unicode_404_internal(self):
        """
        Test the internal code that is used for a 404 page.
        """
        qs = UrlNode.objects.published()

        # This needs a language code that has a fallback to work. Typically,
        # that is 'PARLER_DEFAULT_LANGUAGE_CODE', which is set to 'LANGUAGE_CODE' (en-us) by default.
        self.assertTrue(_get_fallback_language('nl'))

        self.assertRaises(UrlNode.DoesNotExist, lambda: _try_languages('nl', UrlNode.DoesNotExist,
            lambda lang: qs.get_for_path(u'/foo/\xe9\u20ac\xdf\xed\xe0\xf8\xeb\xee\xf1\xfc/', language_code=lang)
        ))


    def test_unicode_404(self):
        """
        Urls with unicode characters should return proper 404 pages, not crash on it.
        """
        # Non existing page
        self.assert404(u'/foo/\xe9\u20ac\xdf\xed\xe0\xf8\xeb\xee\xf1\xfc/')


    def test_admin_redirect(self):
        """
        Urls can end with @admin to be redirected to the admin.
        """
        self.assertRedirects(self.client.get('/@admin'), 'http://testserver/admin/fluent_pages/page/1/', status_code=302)
        self.assertRedirects(self.client.get('/sibling1/@admin'), 'http://testserver/admin/fluent_pages/page/2/', status_code=302)
        self.assertRedirects(self.client.get('/shop/@admin'), 'http://testserver/admin/fluent_pages/page/4/', status_code=302)

        # Anything that doesn't match, is redirected to the URL without @admin suffix
        self.assertRedirects(self.client.get('/unpublished/@admin'), 'http://testserver/unpublished/', status_code=302, target_status_code=404)
        self.assertRedirects(self.client.get('/non-existent/@admin'), 'http://testserver/non-existent/', status_code=302, target_status_code=404)

        # Same also applies to application URLs. Can be extended in the future to resolve to the
        # app page, or the actual object. Currently this is not supported.
        self.assertRedirects(self.client.get('/shop/foobar/@admin'), 'http://testserver/shop/foobar/', status_code=302)


    def test_resolve_reverse(self):
        """
        Test that the resolve/reverse works on the URL conf.
        """
        match1 = resolve('/sibling1/')
        reverse1 = reverse(match1.view_name, args=match1.args, kwargs=match1.kwargs)
        self.assertEqual(reverse1, '/sibling1/')

        match2 = resolve('/sibling1/foo')
        reverse2 = reverse(match2.view_name, args=match2.args, kwargs=match2.kwargs)
        self.assertEqual(reverse2, '/sibling1/foo')

        match3 = resolve('/')
        reverse3 = reverse(match3.view_name, args=match3.args, kwargs=match3.kwargs)
        self.assertEqual(reverse3, '/')

    def test_login_required(self):
        """
        Test that login_required pages redirect to login page when not logged in
        and resolves correctly when logged in.
        """
        # before login
        self.assertRedirects(self.client.get('/sibling2/'), 'http://testserver/accounts/login/?next=/sibling2/', status_code=302)
        self.assertRedirects(self.client.get('/shop2/'), 'http://testserver/accounts/login/?next=/shop2/', status_code=302)
        self.assertRedirects(self.client.get('/shop2/foobar/'), 'http://testserver/accounts/login/?next=/shop2/foobar/', status_code=302)
        self.client.login(username='temporary', password='temporary')
        # after login
        self.assert200('/sibling1/')
        self.assert200('/shop2/')
        self.assert200('/shop2/foobar/')

class UrlDispatcherNonRootTests(AppTestCase):
    """
    Tests for URL resolving with a non-root URL include.
    """

    urls = 'fluent_pages.tests.testapp.urls_nonroot'


    @classmethod
    def setUpTree(cls):
        SimpleTextPage.objects.create(title="Text1", slug="sibling1", status=SimpleTextPage.PUBLISHED, author=cls.user, contents="TEST_CONTENTS")


    def test_urlconf_root(self):
        """
        The dispatcher should support an URLConf where fluent_pages.url is not at the root.
        """
        sibling1 = Page.objects.get_for_path('/sibling1/')  # Stored path is always relative to ROOT

        self.assert200('/pages/sibling1/')
        self.assert404('/sibling1/')
        self.assertEquals(sibling1.get_absolute_url(), '/pages/sibling1/', "UrlNode.get_absolute_url() should other URLConf root into account (got: {0}).".format(sibling1.get_absolute_url()))
        sibling1.save()
        self.assertEquals(sibling1._cached_url, '/sibling1/', "UrlNode keeps paths relative to the include()")
        # NOTE: admin needs to be tested elsewhere for this too.


    def test_admin_redirect(self):
        """
        Urls can end with @admin to be redirected to the admin.
        """
        self.assertRedirects(self.client.get('/pages/sibling1/@admin'), 'http://testserver/admin/fluent_pages/page/1/', status_code=302)
        self.assertRedirects(self.client.get('/pages/non-existent/@admin'), 'http://testserver/pages/non-existent/', status_code=302, target_status_code=404)
