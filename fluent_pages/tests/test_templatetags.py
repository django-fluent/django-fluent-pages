from fluent_pages.tests.utils import AppTestCase
from fluent_pages.tests.testapp.models import SimpleTextPage
import re


class TemplateTagTests(AppTestCase):
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

    def test_menu_404(self):
        response = self.client.get('/404/')
        html = response.content.decode('utf-8')

        # Kind of JSON like, but not really (has trailing commma)
        menu = html[html.find('menu =') + 7:]
        menu = re.sub('\s+', '', menu)

        self.assertEqual(menu,
            """[{'title':"Home','url':"/",'active':false,'children':["""
                """{'title':"Level1a','url':"/level1a/",'active':false},"""
                """{'title':"Level1b','url':"/level1b/",'active':false},"""
            """]},"""
            """{'title':"Root2','url':"/root2/",'active':false},]""")
