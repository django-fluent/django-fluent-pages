import django
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from future.builtins import str
from six import iteritems
from functools import wraps
from django.conf import settings, UserSettingsHolder
from django.core.management import call_command
from django.core.urlresolvers import get_script_prefix, set_script_prefix, reverse
from django.contrib.sites.models import Site
from django.test import TestCase, RequestFactory
from fluent_pages.models.db import UrlNode
from fluent_utils.django_compat import get_user_model
import os

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module  # Python 2.6


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
        super(AppTestCase, cls).setUpClass()

        # Avoid early import, triggers AppCache
        User = get_user_model()

        if cls.install_apps:
            # When running this app via `./manage.py test fluent_pages`, auto install the test app + models.
            run_syncdb = False
            for appname in cls.install_apps:
                if appname not in settings.INSTALLED_APPS:
                    print('Adding {0} to INSTALLED_APPS'.format(appname))
                    settings.INSTALLED_APPS = (appname,) + tuple(settings.INSTALLED_APPS)
                    run_syncdb = True

                    testapp = import_module(appname)

                    # Flush caches
                    if django.VERSION < (1, 9):
                        from django.template.loaders import app_directories
                        from django.db.models import loading
                        loading.cache.loaded = False

                        app_directories.app_template_dirs += (
                            os.path.join(os.path.dirname(testapp.__file__), 'templates'),
                        )
                    else:
                        from django.template.utils import get_app_template_dirs
                        get_app_template_dirs.cache_clear()

            if run_syncdb:
                if django.VERSION < (1, 7):
                    call_command('syncdb', verbosity=0)  # may run south's overlaid version
                else:
                    call_command('migrate', verbosity=0)

        # Create basic objects
        # 1.4 does not create site automatically with the defined SITE_ID, 1.3 does.
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
        pass

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

    def assertFormSuccess(self, request_url, response):
        """
        Assert that the response was a redirect, not a form error.
        """
        self.assertIn(response.status_code, [200, 302])
        if response.status_code != 302:
            context_data = response.context_data
            if 'errors' in context_data:
                errors = response.context_data['errors']
            elif 'form' in context_data:
                errors = context_data['form'].errors
            else:
                raise KeyError("Unknown field for errors in the TemplateResponse!")

            self.assertEqual(response.status_code, 302,
                             "Form errors in calling {0}:\n{1}".format(request_url, errors.as_text()))
        self.assertTrue('/login/?next=' not in response['Location'], "Received login response for {0}".format(request_url))


class AdminTestCase(AppTestCase):
    """
    Testing the creation of mail addresses
    """
    #: The model to test
    model = None
    #: The admin class to test
    admin_class = None

    @classmethod
    def setUpClass(cls):
        super(AdminTestCase, cls).setUpClass()

        # Have a separate site, to avoid dependency on polymorphic wrapping or standard admin configuration
        cls.admin_site = AdminSite()
        cls.admin_site.register(cls.model, cls.admin_class)
        cls.admin_instance = cls.admin_site._registry[cls.model]
        cls.admin_user = User.objects.create_superuser('admin', 'admin@example.org', password='admin')

    def get_add_url(self):
        return reverse(admin_urlname(self.admin_instance.opts, 'add'))

    def get_change_url(self, object_id):
        return reverse(admin_urlname(self.admin_instance.opts, 'change'), args=(object_id,))

    def get_delete_url(self, object_id):
        return reverse(admin_urlname(self.admin_instance.opts, 'delete'), args=(object_id,))

    def admin_post_add(self, formdata):
        """
        Make a direct "add" call to the admin page, circumvening login checks.
        """
        request = self.create_admin_request('post', self.get_add_url(), data=formdata)
        response = self.admin_instance.add_view(request)
        self.assertFormSuccess(request.path, response)
        return response

    def admin_get_change(self, object_id, query=None, **extra):
        """
        Perform a GET request on the admin page
        """
        request = self.create_admin_request('post', self.get_change_url(object_id), data=query, **extra)
        response = self.admin_instance.change_view(request, str(object_id))
        self.assertEqual(response.status_code, 200)
        return response

    def admin_post_change(self, object_id, formdata, **extra):
        """
        Make a direct "add" call to the admin page, circumvening login checks.
        """
        request = self.create_admin_request('post', self.get_change_url(object_id), data=formdata, **extra)
        response = self.admin_instance.change_view(request, str(object_id))
        self.assertFormSuccess(request.path, response)
        return response

    def admin_post_delete(self, object_id, **extra):
        """
        Make a direct "add" call to the admin page, circumvening login checks.
        """
        request = self.create_admin_request('post', self.get_delete_url(object_id), **extra)
        response = self.admin_instance.delete_view(request, str(object_id))
        self.assertEqual(response.status_code, 302, "Form errors in calling {0}".format(request.path))
        return response

    def create_admin_request(self, method, url, data=None, **extra):
        """
        Construct an Request instance for the admin view.
        """
        factory_method = getattr(RequestFactory(), method)

        if data is not None:
            if method != 'get':
                data['csrfmiddlewaretoken'] = 'foo'
            dummy_request = factory_method(url, data=data)
            dummy_request.user = self.admin_user

            # Add the management form fields if needed.
            #base_data = self._get_management_form_data(dummy_request)
            #base_data.update(data)
            #data = base_data

        request = factory_method(url, data=data, **extra)
        request.COOKIES[settings.CSRF_COOKIE_NAME] = 'foo'

        # Add properties which middleware would typically do
        request.session = {}
        request.user = self.admin_user
        MessageMiddleware().process_request(request)
        return request

    def _get_management_form_data(self, request):
        """
        Return the formdata that the management forms need.
        """
        inline_instances = self.admin_instance.get_inline_instances(request)
        forms = []
        for inline_instance in inline_instances:
            FormSet = inline_instance.get_formset(request)
            formset = FormSet(instance=self.admin_instance.model())
            forms.append(formset.management_form)

        # In a primitive way, get the form fields.
        # This is not exactly the same as a POST, since that runs through clean()
        formdata = {}
        for form in forms:
            for boundfield in form:
                formdata[boundfield.html_name] = boundfield.value()

        return formdata


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
            for key, new_value in iteritems(self.options):
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
