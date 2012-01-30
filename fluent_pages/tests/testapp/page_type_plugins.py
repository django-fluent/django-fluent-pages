from fluent_pages.extensions import page_type_pool, PageTypePlugin
from fluent_pages.tests.testapp.models import PlainTextPage


class PlainTextPagePlugin(PageTypePlugin):
    model = PlainTextPage
    render_template = "testapp/plaintextpage.html"


page_type_pool.register(PlainTextPagePlugin)
