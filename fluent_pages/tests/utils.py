import os
from importlib import import_module

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import get_script_prefix, set_script_prefix
from fluent_pages.models.db import UrlNode
from future.builtins import str


class AppTestCase(TestCase):
    """
    Tests for URL resolving.
    """
    user = None
    install_apps = (
        'fluent_pages.tests.testapp',
    )

    @classmethod
    def setUpClass(cls):
        if cls.install_apps:
            # When running this app via `./manage.py test fluent_pages`, auto install the test app + models.
            run_migrate = False
            for appname in cls.install_apps:
                if appname not in settings.INSTALLED_APPS:
                    print('Adding {0} to INSTALLED_APPS'.format(appname))
                    settings.INSTALLED_APPS = (appname,) + tuple(settings.INSTALLED_APPS)
                    run_migrate = True

                    testapp = import_module(appname)

                    # Flush caches
                    from django.template.utils import get_app_template_dirs
                    get_app_template_dirs.cache_clear()

            if run_migrate:
                call_command('migrate', verbosity=0)

        # This also runs setUpTestData
        super(AppTestCase, cls).setUpClass()

    @classmethod
    def setUpTestData(cls):
        # Avoid early import, triggers AppCache
        User = get_user_model()

        # Create basic objects
        Site.objects.get_or_create(id=settings.SITE_ID, defaults=dict(domain='django.localhost', name='django at localhost'))
        cls.user, _ = User.objects.get_or_create(is_superuser=True, is_staff=True, username="fluent-pages-admin")

        # Create tree.
        # Reset data first because the testcase class setup runs outside the transaction
        UrlNode.objects.all().delete()
        cls.setUpTree()

    @classmethod
    def setUpTree(cls):
        """
        Create all the pages.
        """

    def assert200(self, url, msg_prefix=''):
        """
        Test that an URL exists.
        """
        if msg_prefix:
            msg_prefix += ": "
        self.assertEqual(self.client.get(url).status_code, 200, str(msg_prefix) + u"Page at {0} should be found.".format(url))

    def assert404(self, url, msg_prefix=''):
        """
        Test that an URL does not exist.
        """
        if msg_prefix:
            msg_prefix += ": "
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404, str(msg_prefix) + u"Page at {0} should return 404, got {1}.".format(url, response.status_code))


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
