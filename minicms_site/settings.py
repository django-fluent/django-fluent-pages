# Django settings for minicms project.
import sys
import os

DEBUG          = True
TEMPLATE_DEBUG = DEBUG

# My custom features
ENABLE_PYDEV   = DEBUG
ENABLE_TOOLBAR = False
ENABLE_ADMIN   = True


# People who receive 500 errors
ADMINS = (
    ('Diederik van der Boor', 'vdboor@codingdomain.com'),
)

# People who receive 404 errors
MANAGERS = ADMINS


## --- Internal settings

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE':   'mysql',      # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME':     'minicms',     # Or path to database file if using sqlite3.
        'USER':     'minicms',     # Not used with sqlite3.
        'PASSWORD': 'djangotest', # Not used with sqlite3.
    },
}


# Language codes
USE_I18N = True                   # False for optimizations
TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'en-us'

# Extra autodetection
_projectDir = os.path.dirname(os.path.realpath(__file__))

# Paths
MEDIA_ROOT  = _projectDir + '/media/'
MEDIA_URL   = '/media/'        # Must end with /

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2x@x)9^etcc3(+6ow74=hh0p=fbzbxpz5)h=s=8qv4kt2c)ze#'



## --- Plugin components

# Extend the python path, to include projects at the same level.
_appsPath = os.path.dirname(_projectDir)
if _appsPath not in sys.path:
    sys.path.append(_appsPath)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    # All site parts should preferably be separate (reusable) apps
    'ecms',
    'mptt',
)

ROOT_URLCONF = 'minicms_site.urls'

TEMPLATE_DIRS = (
    _projectDir + '/templates/'       # Absolute paths, always forward slashes
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.auth',
                               'django.core.context_processors.i18n',
                               'django.core.context_processors.media',
                               'django.core.context_processors.request',               # Required by admin_tools
                               'django.contrib.messages.context_processors.messages',  # Django 1.2
                              )


## --- Optional Features

ADMIN_MEDIA_PREFIX = '/admin-media/'
INTERNAL_IPS = ('127.0.0.1',)

if DEBUG:
    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)

if ENABLE_ADMIN:
    INSTALLED_APPS += ('admin_tools.theming',
                       'admin_tools.menu',
                       'admin_tools.dashboard',
                       'django.contrib.admin',
                       'django.contrib.admindocs',
                      )

if ENABLE_TOOLBAR:
    INSTALLED_APPS     += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

