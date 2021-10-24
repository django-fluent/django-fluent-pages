"""
Just a pretty normal model definition of a simple "shop".
"""
from django.db import models

from fluent_pages.models import Page


class ProductCategory(models.Model):
    title = models.CharField("Title", max_length=200)
    slug = models.SlugField("Slug")

    class Meta:
        verbose_name = "Productcategory"
        verbose_name_plural = "Productcategories"
        ordering = ("title",)

    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory, on_delete=models.PROTECT, verbose_name="Category", related_name="products"
    )
    title = models.CharField("Title", max_length=200)
    slug = models.SlugField("Slug")

    description = models.TextField("Description")
    price = models.DecimalField("Price", max_digits=10, decimal_places=2)
    # photo = models.ImageField('Photo', blank=True, upload_to='uploads/productphotos')

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("title",)

    def __str__(self):
        return self.title


class ProductCategoryPage(Page):
    """
    The database model for the custom pagetype.
    """

    product_category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Product category page"
        verbose_name_plural = "Product category pages"
