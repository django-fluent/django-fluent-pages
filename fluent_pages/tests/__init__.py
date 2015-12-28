"""
Test suite for fluent-pages
"""
import django
if django.VERSION < (1,6):
    # Expose for Django 1.5 and below (before DiscoverRunner)
    from .test_urldispatcher import UrlDispatcherTests, UrlDispatcherNonRootTests
    from .test_menu import MenuTests
    from .test_modeldata import ModelDataTests
    from .test_plugins import PluginTests, PluginUrlTests
    from .test_templatetags import TemplateTagTests
