from django.http import HttpResponse
from fluent_pages.extensions import PageTypePlugin, page_type_pool
from fluent_pages.tests.testapp.models import ChildTypesPage, PlainTextFile, SimpleTextPage, WebShopPage


@page_type_pool.register
class SimpleTextPagePlugin(PageTypePlugin):
    """
    Place a simple page in the page tree.
    """
    model = SimpleTextPage
    render_template = "testapp/simpletextpage.html"


@page_type_pool.register
class ChildTypesPagePlugin(PageTypePlugin):
    """
    Place a simple page in the page tree.
    """
    model = ChildTypesPage
    render_template = "testapp/simpletextpage.html"

    child_types = ['self', 'SimpleTextPage', 'testapp.PlainTextFile',
                   WebShopPage]


@page_type_pool.register
class PlainTextFilePlugin(PageTypePlugin):
    """
    Place a simple page in the page tree.
    """
    model = PlainTextFile
    is_file = True

    def get_response(self, request, textfile, **kwargs):
        return HttpResponse(
            content=textfile.content,
            content_type='text/plain',
        )


@page_type_pool.register
class WebShopPagePlugin(PageTypePlugin):
    """
    Place a "webshop" node in the page tree
    """
    model = WebShopPage
    urls = 'fluent_pages.tests.testapp.urls_webshop'
