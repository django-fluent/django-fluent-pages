# Settings file to allow parsing API documentation of Django modules,
# and provide defaults to use in the documentation.
#
# This file is placed in a subdirectory,
# so the docs root won't be detected by find_packages()
import os

# Display sane URLs in the docs:
STATIC_URL = '/static/'

# Required to pass module tests
FLUENT_PAGES_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates/')

# Required by Django
SECRET_KEY = 'foo'
SITE_ID = 1
