from fluent_pages.extensions import page_type_pool, PageTypePlugin
from fluent_pages.tests.testapp.models import SimpleTextPage, WebShopPage


@page_type_pool.register
class SimpleTextPagePlugin(PageTypePlugin):
    """
    Place a simple page in the page tree.
    """
    model = SimpleTextPage
    render_template = "testapp/simpletextpage.html"


@page_type_pool.register
class WebShopPagePlugin(PageTypePlugin):
    """
    Place a "webshop" node in the page tree
    """
    model = WebShopPage
    urls = 'fluent_pages.tests.testapp.urls_webshop'
