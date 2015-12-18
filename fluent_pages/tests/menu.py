from fluent_pages.models import Page
from fluent_pages.models.navigation import PageNavigationNode
from fluent_pages.tests.utils import AppTestCase
from fluent_pages.tests.testapp.models import SimpleTextPage


class MenuTests(AppTestCase):
    """
    Tests for URL resolving.
    """
    root_url = '/'
    subpage1_url = '/test_subpage1/'

    @classmethod
    def setUpTree(cls):
        root = SimpleTextPage.objects.create(title="Home", slug="home", status=SimpleTextPage.PUBLISHED, author=cls.user, override_url='/')
        root2 = SimpleTextPage.objects.create(title="Root2", slug="root2", status=SimpleTextPage.PUBLISHED, author=cls.user)

        level1a = SimpleTextPage.objects.create(title="Level1a", slug="level1a", parent=root, status=SimpleTextPage.PUBLISHED, author=cls.user)
        level1b = SimpleTextPage.objects.create(title="Level1b", slug="level1b", parent=root, status=SimpleTextPage.PUBLISHED, author=cls.user)

    def test_navigation(self):
        """
        The API should return the top level
        """
        menu = list(Page.objects.toplevel_navigation())
        self.assertEqual(len(menu), 2)
        self.assertEqual(menu[0].slug, 'home')
        self.assertEqual(menu[1].slug, 'root2')

    def test_current_item(self):
        """
        The API should pass the current page to it's queryset.
        """
        current_page = Page.objects.get(translations__slug='root2')

        menu = list(Page.objects.toplevel_navigation(current_page=current_page))
        self.assertEqual(menu[0].slug, 'home')
        self.assertEqual(menu[1].slug, 'root2')
        self.assertEqual(menu[0].is_current, False)
        self.assertEqual(menu[1].is_current, True)

        # NOTE: does not support sub pages.

    def test_menu_items(self):
        """
        The menu API should return the active item.
        """
        current_page = Page.objects.get(translations__slug='root2')

        nav = Page.objects.toplevel_navigation(current_page=current_page)
        menu = [PageNavigationNode(page, current_page=current_page) for page in nav]

        # Test structure
        self.assertEqual(menu[0].slug, 'home')
        self.assertEqual(menu[1].slug, 'root2')

        # PageNavigationNode.parent should deal with missing get_parent() attribute:
        self.assertEqual(menu[0].parent, None)
        self.assertEqual(menu[1].parent, None)

        # Test active state
        self.assertEqual(menu[0].is_active, False)
        self.assertEqual(menu[1].is_active, True)

    def test_sub_menu_items(self):
        """
        The menu API should return the active item.
        """
        current_page = Page.objects.get(translations__slug='level1a')

        nav = Page.objects.toplevel_navigation(current_page=current_page)
        menu = [PageNavigationNode(page, current_page=current_page) for page in nav]

        # Test structure
        self.assertEqual(menu[0].slug, 'home')
        self.assertEqual(menu[1].slug, 'root2')

        self.assertNumQueries(0, lambda: menu[0].has_children)
        self.assertNumQueries(1, lambda: list(menu[0].children))
        self.assertNumQueries(0, lambda: list(menu[1].children))

        self.assertEqual(menu[0].has_children, True)
        self.assertEqual(menu[1].has_children, False)

        children = list(menu[0].children)
        self.assertEqual(children[0].slug, 'level1a')
        self.assertEqual(children[1].slug, 'level1b')

        # Test reverse structure
        self.assertEqual(children[0].parent, menu[0])

        # Test active states
        self.assertEqual(menu[0].is_active, False)
        self.assertEqual(menu[1].is_active, False)

        self.assertEqual(children[0].is_active, True)
        self.assertEqual(children[1].is_active, False)
