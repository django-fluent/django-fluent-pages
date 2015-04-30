"""
Internal library for Django compatibility.
"""
from django.template import Library
from fluent_utils.django_compat import get_meta_model_name

register = Library()

register.filter('get_meta_model_name', get_meta_model_name)

try:
    from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
except ImportError:
    # Django 1.5:
    @register.simple_tag(takes_context=True)
    def add_preserved_filters(context, url, popup=False, to_field=None):
        return url
