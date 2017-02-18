from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from fluent_pages.models import Page
from fluent_pages.tests.utils import AppTestCase
from fluent_pages.tests.testapp.models import (
    SimpleTextPage, PlainTextFile, WebShopPage, ChildTypesPage)
from fluent_utils.django_compat import get_user_model

class AdminTests(AppTestCase):

    def setUp(self):
        # Need to make sure that django-parler's cache isn't reused,
        # because the transaction is rolled back on each test method.
        cache.clear()
        # Need to make a staff member and login
        User = get_user_model()
        self.username = 'a'
        self.email = 'ab@example.com'
        self.password = 'b'
        self.test_user = User.objects.create_user(self.username, self.email, self.password)
        self.test_user.is_staff = True
        self.test_user.save()
        login = self.client.login(username=self.username, password=self.password)
        self.assertEqual(login, True)

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

    def move_mode(self):
        """Make root a child of root2"""
        resp = self.client.post('/admin/fluent_pages/page/api/node-moved/', {
            'moved_id': self.root.id,
            'target_id': self.root2.id,
            'position': 'inside',
            'previous_parent_id': 0
        })

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
        self.move_mode()
        # refresh objects
        self.root = Page.objects.get(pk=self.root.pk)
        self.root2 = Page.objects.get(pk=self.root2.pk)

        self.assertFalse(self.root.url.startswith(self.root2.url))

