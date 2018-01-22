from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from fluent_pages.models import Page
from fluent_pages.tests.testapp.models import ChildTypesPage, PlainTextFile, SimpleTextPage, WebShopPage
from fluent_pages.tests.utils import AppTestCase


class AdminTests(AppTestCase):

    def setUp(self):
        # Need to make sure that django-parler's cache isn't reused,
        # because the transaction is rolled back on each test method.
        cache.clear()

        # Adding a superuser, to circumvent any permission checks on moving nodes.
        User = get_user_model()
        self.test_user = User.objects.create_superuser('a', 'ab@example.com', 'b')
        self.test_user.save()
        self.client.force_login(self.test_user)

    @classmethod
    def setUpTree(cls):
        cls.root = SimpleTextPage.objects.create(title="Home", slug="home", status=SimpleTextPage.PUBLISHED, author=cls.user)
        cls.root2 = ChildTypesPage.objects.create(title="Root2", slug="root2", status=ChildTypesPage.PUBLISHED, author=cls.user)

    def test_child_types(self):
        """test that all child types are created and correct"""
        ids = set([
            self.root.polymorphic_ctype_id,
            self.root2.polymorphic_ctype_id,
            ContentType.objects.get_for_model(PlainTextFile).id,
            ContentType.objects.get_for_model(WebShopPage).id,
        ])
        childtypes = set(self.root2.get_child_types())
        self.assertEqual(len(ids), len(ids | childtypes))

    def move_mode(self, expect_status=200):
        """Make root a child of root2"""
        response = self.client.post('/admin/fluent_pages/page/api/node-moved/', {
            'moved_id': self.root.id,
            'target_id': self.root2.id,
            'position': 'inside',
            'previous_parent_id': None
        })
        self.assertEqual(response.status_code, expect_status)

    def test_allowed(self):
        """"test the move with no modifications to child types"""
        # try the move
        self.move_mode()
        # refresh objects
        self.root = Page.objects.get(pk=self.root.pk)
        self.root2 = Page.objects.get(pk=self.root2.pk)

        self.assertTrue(self.root.url.startswith(self.root2.url))

    def test_not_allowed(self):
        """"test the move after removing child from allowed child types"""
        # modify the childtypes cache
        page_key = self.root2.page_key
        self.root2._PolymorphicMPTTModel__child_types[page_key].remove(
            self.root.polymorphic_ctype_id)
        # try the move
        self.move_mode(expect_status=409)
        # refresh objects
        self.root = Page.objects.get(pk=self.root.pk)
        self.root2 = Page.objects.get(pk=self.root2.pk)

        self.assertFalse(self.root.url.startswith(self.root2.url))
