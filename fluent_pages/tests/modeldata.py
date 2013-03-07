from fluent_pages.models import Page
from fluent_pages.tests.utils import AppTestCase
from fluent_pages.tests.testapp.models import SimpleTextPage, WebShopPage


class ModelDataTests(AppTestCase):
    """
    Tests for URL resolving.
    """
    root_url = '/'
    subpage1_url = '/test_subpage1/'


    @classmethod
    def setUpTree(cls):
        root = SimpleTextPage.objects.create(title="Home", slug="home", status=SimpleTextPage.PUBLISHED, author=cls.user, override_url='/')
        draft1 = SimpleTextPage.objects.create(title="Draft1", slug="draft1", parent=root, status=SimpleTextPage.DRAFT, author=cls.user)
        level1 = SimpleTextPage.objects.create(title="Level1", slug="level1", parent=root, status=SimpleTextPage.PUBLISHED, author=cls.user)
        level2 = SimpleTextPage.objects.create(title="Level2", slug="level2", parent=level1, status=SimpleTextPage.PUBLISHED, author=cls.user)
        root2 = SimpleTextPage.objects.create(title="Root2", slug="root2", status=SimpleTextPage.PUBLISHED, author=cls.user)
        shop = WebShopPage.objects.create(title="Shop1", slug="shop", status=WebShopPage.PUBLISHED, author=cls.user)


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
