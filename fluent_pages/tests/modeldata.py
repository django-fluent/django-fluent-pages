import django
from django.core.exceptions import ValidationError
from fluent_pages.models import Page
from fluent_pages.models.fields import PageTreeForeignKey
from fluent_pages.models.managers import UrlNodeQuerySet
from fluent_pages.tests.utils import AppTestCase
from fluent_pages.tests.testapp.models import SimpleTextPage, PlainTextFile, WebShopPage


class ModelDataTests(AppTestCase):
    """
    Tests for URL resolving.
    """
    root_url = '/'
    subpage1_url = '/test_subpage1/'


    @classmethod
    def setUpTree(cls):
        cls.root = SimpleTextPage.objects.create(title="Home", slug="home", status=SimpleTextPage.PUBLISHED, author=cls.user, override_url='/')
        cls.draft1 = SimpleTextPage.objects.create(title="Draft1", slug="draft1", parent=cls.root, status=SimpleTextPage.DRAFT, author=cls.user)
        cls.level1 = SimpleTextPage.objects.create(title="Level1", slug="level1", parent=cls.root, status=SimpleTextPage.PUBLISHED, author=cls.user)
        cls.level2 = SimpleTextPage.objects.create(title="Level2", slug="level2", parent=cls.level1, status=SimpleTextPage.PUBLISHED, author=cls.user)
        cls.root2 = SimpleTextPage.objects.create(title="Root2", slug="root2", status=SimpleTextPage.PUBLISHED, author=cls.user)
        cls.shop = WebShopPage.objects.create(title="Shop1", slug="shop", status=WebShopPage.PUBLISHED, author=cls.user)


    def test_get_for_path(self):
        """
        The get for path should work strictly on the path.
        """
        self.assertEqual(Page.objects.get_for_path('/'), self.root)
        self.assertEqual(Page.objects.get_for_path('/draft1/'), self.draft1)
        self.assertEqual(Page.objects.get_for_path('/level1/level2/'), self.level2)

        # Any inaccuracies should raise errors
        self.assertRaises(Page.DoesNotExist, lambda: Page.objects.get_for_path('/level1/level2'))
        self.assertRaises(Page.DoesNotExist, lambda: Page.objects.get_for_path('level1/level2/'))
        self.assertRaises(Page.DoesNotExist, lambda: Page.objects.get_for_path('level1/level2'))


    def test_best_match_for_path(self):
        """
        The best match should return the first match, but never the '/'.
        """
        self.assertEqual(Page.objects.best_match_for_path('/level1/level2/foo/bar/'), self.level2)
        self.assertEqual(Page.objects.best_match_for_path('/level1/level2/noslash.txt'), self.level2)

        # If the root node has custom URLs support, that should also work:
        self.assertEqual(Page.objects.best_match_for_path('/virtual/root-path/'), self.root)

        # If there is no slash, there is still a best match.
        # However, it can't be the level2 itself because that URL has a slash at it's end.
        # The URL dispatcher handles APPEND_SLASH behaviour, not the model API.
        self.assertEqual(Page.objects.best_match_for_path('/level1/level2'), self.level1)

        # Any inaccuracies should raise errors
        self.assertRaises(Page.DoesNotExist, lambda: Page.objects.best_match_for_path('level1/level2/'))
        self.assertRaises(Page.DoesNotExist, lambda: Page.objects.best_match_for_path('level1/level2'))


    def test_split_path_levels(self):
        """
        Test the splitting of URL paths, which is the core of best_match_for_path()
        """
        # Test standard path levels
        self.assertEqual(Page.objects._split_path_levels('/level1/level2/'), ['/', '/level1/', '/level1/level2/'])

        # Not adding a slash is reflected in the results
        self.assertEqual(Page.objects._split_path_levels('/level1/level2/noslash.txt'), ['/', '/level1/', '/level1/level2/', '/level1/level2/noslash.txt'])
        self.assertEqual(Page.objects._split_path_levels('/level1/level2'), ['/', '/level1/', '/level1/level2'])

        # Garbage in, garbage out
        self.assertEqual(Page.objects._split_path_levels('level1/level2'), ['level1/', 'level1/level2'])


    def test_polymorphic(self):
        """
        The API should return the polymorphic objects
        """
        # Getting single objects
        level1 = Page.objects.get_for_path('/level1/')
        shop = Page.objects.get_for_path('/shop/')
        self.assertIsInstance(level1, SimpleTextPage)
        self.assertIsInstance(shop, WebShopPage)

        # Same for lists
        pages = list(Page.objects.published().filter(slug__in=('level1', 'shop')).order_by('slug'))
        self.assertIsInstance(pages[0], SimpleTextPage)
        self.assertIsInstance(pages[1], WebShopPage)


    def test_related_tree_manager(self):
        """
        The tree manager should get the same abilities as the original manager.
        This was broken in django-mptt 0.5.2
        """
        self.assertIs(type(Page.objects.get_for_path('/').children.all()), UrlNodeQuerySet)  # This broke with some django-mptt 0.5.x versions
        self.assertEqual(Page.objects.get_for_path('/').children.in_navigation()[0].slug, 'level1')


    def test_move_root(self):
        """
        Moving the root node should update all child node URLs. (they are precalculated/cached in the DB)
        """
        # Get start situation
        root = SimpleTextPage.objects.get(override_url='/')
        level1 = SimpleTextPage.objects.get(slug='level1')
        level2 = SimpleTextPage.objects.get(slug='level2')
        self.assertEquals(level1.get_absolute_url(), '/level1/')
        self.assertEquals(level2.get_absolute_url(), '/level1/level2/')

        # Change root
        root.override_url = '/new_root/'
        root.save()

        # Check result
        level1 = SimpleTextPage.objects.get(slug='level1')
        level2 = SimpleTextPage.objects.get(slug='level2')
        self.assertEquals(level1.get_absolute_url(), '/new_root/level1/')
        self.assertEquals(level2.get_absolute_url(), '/new_root/level1/level2/')

        # TODO: note that things like .filter().update() won't work on override_url and slug properties.


    def test_rename_slug(self):
        """
        Renaming a slug should affect the nodes below.
        """
        level1 = SimpleTextPage.objects.get(slug='level1')
        level1.slug = 'level1_b'
        level1.save()

        level1 = SimpleTextPage.objects.get(pk=level1.pk)
        level2 = SimpleTextPage.objects.get(slug='level2')
        self.assertEquals(level1.get_absolute_url(), '/level1_b/')
        self.assertEquals(level2.get_absolute_url(), '/level1_b/level2/')


    def test_change_parent(self):
        """
        Moving a tree to a new parent should update their URLs
        """
        root2 = SimpleTextPage.objects.get(slug='root2')
        level1 = SimpleTextPage.objects.get(slug='level1')
        level1.parent = root2
        level1.save()

        level1 = SimpleTextPage.objects.get(pk=level1.pk)
        level2 = SimpleTextPage.objects.get(slug='level2')
        self.assertEquals(level1.get_absolute_url(), '/root2/level1/')
        self.assertEquals(level2.get_absolute_url(), '/root2/level1/level2/')


    def test_duplicate_slug(self):
        """
        At the model level, a duplicate slug is automatically renamed.
        """
        page1 = SimpleTextPage.objects.create(slug='dup-slug', author=self.user)
        page2 = SimpleTextPage.objects.create(slug='dup-slug', author=self.user)
        page3 = SimpleTextPage.objects.create(slug='dup-slug', author=self.user)

        self.assertEqual(page1.slug, 'dup-slug')
        self.assertEqual(page2.slug, 'dup-slug-2')
        self.assertEqual(page3.slug, 'dup-slug-3')

        # The duplicates should be detected per level,
        # and update when the page is moved.
        page4 = SimpleTextPage.objects.create(slug='dup-slug', parent=page3, author=self.user)
        self.assertEqual(page4.slug, 'dup-slug')

        page4.parent = None
        page4.save()
        self.assertEqual(page4.slug, 'dup-slug-4')

        # Renaming a slug also works
        page5 = SimpleTextPage.objects.create(slug='unique-slug', author=self.user)
        self.assertEqual(page5.slug, 'unique-slug')

        page5.slug = 'dup-slug'
        page5.save()
        self.assertEqual(page5.slug, 'dup-slug-5')


    def test_file_model_urls(self):
        """
        When a plugin type is marked as "file" behave accordingly.
        """
        text_file = PlainTextFile.objects.create(slug='README', status=PlainTextFile.PUBLISHED, author=self.user, content="This is the README")
        self.assertEqual(text_file.get_absolute_url(), '/README')  # No slash!

        text_file2 = PlainTextFile.objects.create(slug='README', parent=self.level1, status=PlainTextFile.PUBLISHED, author=self.user, content="This is the README")
        self.assertEqual(text_file2.get_absolute_url(), '/level1/README')  # No slash!


    def test_file_model_parent(self):
        """
        A file model does not allow children.
        """
        text_file = PlainTextFile.objects.create(slug='README', status=PlainTextFile.PUBLISHED, author=self.user, content="This is the README")
        text_file2 = PlainTextFile(slug='AUTHORS', parent=text_file, author=self.user, content='AUTHORS file')

        # Note that .save() doesn't validate, as per default Django behavior.
        if django.VERSION >= (1, 4):
            self.assertRaisesMessage(ValidationError, PageTreeForeignKey.default_error_messages['no_children_allowed'], lambda: text_file2.full_clean())
        else:
            self.assertRaises(ValidationError, lambda: text_file2.full_clean())
