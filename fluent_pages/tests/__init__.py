"""
Test suite for fluent-pages
"""

# Import all tests
from .urldispatcher import UrlDispatcherTests, UrlDispatcherNonRootTests
from .menu import MenuTests
from .modeldata import ModelDataTests
from .plugins import PluginTests, PluginUrlTests
from .templatetags import TemplateTagTests
