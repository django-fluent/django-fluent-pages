from django.conf.urls.defaults import patterns, url
from fluent_pages.extensions import PageTypePlugin, page_type_pool
from simpleshop.models import ProductCategoryPage


class ProductCategoryPagePlugin(PageTypePlugin):
    """"
    A new pagetype plugin that binds the rendering and model together.
    """
    model = ProductCategoryPage
    render_template = "products/productcategorypage.html"
    urls = patterns('simpleshop.views',
        url('^(?P<slug>[^/]+)/$', 'product_details'),
    )


page_type_pool.register(ProductCategoryPagePlugin)
