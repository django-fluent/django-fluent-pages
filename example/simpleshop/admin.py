from django.contrib import admin

from simpleshop.models import Product, ProductCategory


class ProductCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class ProductAdmin(admin.ModelAdmin):
    """
    A simple admin interface for the product administration.
    """
    list_display = ('title', 'price', 'category')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
