from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from simpleshop.models import Product


def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_details.html', {
        'product': product
    })
