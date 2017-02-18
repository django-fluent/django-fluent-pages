from django.conf.urls import url
from fluent_pages.extensions import PageTypePlugin, page_type_pool

from simpleshop.models import ProductCategoryPage
from simpleshop.views import product_details


@page_type_pool.register
class ProductCategoryPagePlugin(PageTypePlugin):
    """"
    A new pagetype plugin that binds the rendering and model together.
    """
    model = ProductCategoryPage
    render_template = "products/productcategorypage.html"
    urls = [
        url('^(?P<slug>[^/]+)/$', product_details),
    ]
