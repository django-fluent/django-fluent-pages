from functools import wraps
from django.conf import settings, UserSettingsHolder
from django.core.management import call_command
from django.core.urlresolvers import get_script_prefix, set_script_prefix
from django.contrib.sites.models import Site
from django.db.models import loading
from django.template.loaders import app_directories
from django.test import TestCase
from fluent_pages.models.db import UrlNode
from fluent_pages.tests import testapp
import os

# support for custom User models in Django 1.5+
try:
    from django.contrib.auth import get_user_model
except ImportError:  # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()


class AppTestCase(TestCase):
    """
    Tests for URL resolving.
    """
    user = None


    @classmethod
    def setUpClass(cls):
        if 'fluent_pages.tests.testapp' not in settings.INSTALLED_APPS:
            # When running this app via `./manage.py test fluent_pages`, auto install the test app + models.
            print 'Adding fluent_pages.tests.testapp to INSTALLED_APPS'
            settings.INSTALLED_APPS += ('fluent_pages.tests.testapp',)

            # Flush caches
            loading.cache.loaded = False
            app_directories.app_template_dirs += (
                os.path.join(os.path.dirname(testapp.__file__), 'templates'),
            )

            call_command('syncdb', verbosity=0)  # may run south's overlaid version

        # Create basic objects
        # 1.4 does not create site automatically with the defined SITE_ID, 1.3 does.
        Site.objects.get_or_create(id=settings.SITE_ID, defaults=dict(domain='django.localhost', name='django at localhost'))
        cls.user, _ = User.objects.get_or_create(is_superuser=True, is_staff=True, username="admin")

        # Create tree.
        # Reset data first because the testcase class setup runs outside the transaction
        UrlNode.objects.all().delete()
        cls.setUpTree()


    @classmethod
    def setUpTree(cls):
        """
        Create all the pages.
        """
        pass


    def assert200(self, url, msg_prefix=''):
        """
        Test that an URL exists.
        """
        if msg_prefix:
            msg_prefix += ": "
        self.assertEquals(self.client.get(url).status_code, 200, unicode(msg_prefix) + u"Page at {0} should be found.".format(url))


    def assert404(self, url, msg_prefix=''):
        """
        Test that an URL does not exist.
        """
        if msg_prefix:
            msg_prefix += ": "
        self.assertEquals(self.client.get(url).status_code, 404, unicode(msg_prefix) + u"Page at {0} should return 404.".format(url))


try:
    from django.test.utils import override_settings  # Django 1.4
except ImportError:
    class override_settings(object):
        """
        Acts as either a decorator, or a context manager. If it's a decorator it
        takes a function and returns a wrapped function. If it's a contextmanager
        it's used with the ``with`` statement. In either event entering/exiting
        are called before and after, respectively, the function/block is executed.
        """
        def __init__(self, **kwargs):
            self.options = kwargs
            self.wrapped = settings._wrapped

        def __enter__(self):
            self.enable()

        def __exit__(self, exc_type, exc_value, traceback):
            self.disable()

        def __call__(self, test_func):
            from django.test import TransactionTestCase
            if isinstance(test_func, type) and issubclass(test_func, TransactionTestCase):
                original_pre_setup = test_func._pre_setup
                original_post_teardown = test_func._post_teardown
                def _pre_setup(innerself):
                    self.enable()
                    original_pre_setup(innerself)
                def _post_teardown(innerself):
                    original_post_teardown(innerself)
                    self.disable()
                test_func._pre_setup = _pre_setup
                test_func._post_teardown = _post_teardown
                return test_func
            else:
                @wraps(test_func)
                def inner(*args, **kwargs):
                    with self:
                        return test_func(*args, **kwargs)
            return inner

        def enable(self):
            override = UserSettingsHolder(settings._wrapped)
            for key, new_value in self.options.items():
                setattr(override, key, new_value)
            settings._wrapped = override

        def disable(self):
            settings._wrapped = self.wrapped


class script_name(override_settings):
    """
    Simulate that the application has a different root folder, expressed by the ``SCRIPT_NAME`` variable.
    This can happen for example, by using ``WSGIScriptAlias /subfolder`` for the Django site.
    It causes ``request.path`` and ``request.path_info`` to differ, making it important to use the right one.
    """

    def __init__(self, newpath):
        if newpath[0] != '/' or newpath[-1] != '/':
            raise ValueError("Path needs to have slashes at both ends.")

        new_settings = {
            'FORCE_SCRIPT_NAME': newpath
        }

        # Auto adjust media urls if they are not set already.
        newpath_noslash = newpath.rstrip('/')
        if settings.MEDIA_URL and settings.MEDIA_URL[0] == '/' and not settings.MEDIA_URL.startswith(newpath):
            new_settings['MEDIA_URL'] = newpath_noslash + settings.MEDIA_URL
        if settings.STATIC_URL and settings.STATIC_URL[0] == '/' and not settings.STATIC_URL.startswith(newpath):
            new_settings['STATIC_URL'] = newpath_noslash + settings.STATIC_URL

        super(script_name, self).__init__(**new_settings)
        self.newpath = newpath
        self.oldprefix = get_script_prefix()


    def enable(self):
        super(script_name, self).enable()
        set_script_prefix(self.newpath)


    def disable(self):
        super(script_name, self).disable()
        set_script_prefix(self.oldprefix)
