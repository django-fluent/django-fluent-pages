from django.contrib import admin
from simpleshop.models import Product, ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    A simple admin interface for the product administration.
    """

    list_display = ("title", "price", "category")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("title",)}


