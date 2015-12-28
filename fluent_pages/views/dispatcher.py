"""
The view to display CMS content.
"""
import re

from future.builtins import str
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import Resolver404, reverse, resolve, NoReverseMatch, get_script_prefix
from django.http import Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.template.response import TemplateResponse
from django.utils import translation
from django.views.generic.base import View
from django.views.generic import RedirectView

from fluent_pages import appsettings
from fluent_pages.models import UrlNode
from fluent_pages.models.utils import prefill_parent_site


# NOTE:
# Since the URLconf of this module acts like a catch-all to serve files (e.g. paths without /),
# the CommonMiddleware will not detect that the path could need an extra slash.
# That logic also has to be implemented here.

class GetPathMixin(View):

    def get_path(self):
        """
        Return the path argument of the view.
        """
        if 'path' in self.kwargs:
            # Starting slash is removed by URLconf, restore it.
            return '/' + (self.kwargs['path'] or '')
        else:
            # Path from current script prefix
            return self.request.path_info

    def get_language(self):
        """
        Return the language to display in this view.
        """
        return translation.get_language()  # Assumes that middleware has set this properly.


class CmsPageDispatcher(GetPathMixin, View):
    """
    The view which displays a CMS page.
    This is not a ``DetailsView`` by design, as the rendering is redirected to the page type plugin.

    Regular pages are rendered using :func:`fluent_pages.extensions.PageTypePlugin.get_response`.
    """
    model = UrlNode
    prefetch_translations = appsettings.FLUENT_PAGES_PREFETCH_TRANSLATIONS

    def get(self, request, **kwargs):
        """
        Display the page in a GET request.
        """
        self.language_code = self.get_language()
        self.path = self.get_path()

        # See which view returns a valid response.
        for func in (
            self._try_node,
            self._try_node_redirect,
            self._try_appnode,
            self._try_append_slash_redirect
        ):
            response = func()
            if response is not None:
                return response

        return self._page_not_found()

    def post(self, request, **kwargs):
        """
        Allow POST requests (for forms) to the page.
        """
        return self.get(request, **kwargs)

    def _page_not_found(self):
        # Since this view acts as a catch-all, give better error messages
        # when mistyping an admin URL. Don't mention anything about CMS pages in /admin.
        try:
            full_path = get_script_prefix() + self.path.lstrip('/')
            if full_path.startswith(reverse('admin:index')):
                raise Http404(u"No admin page found at '{0}'\n(raised by fluent_pages catch-all).".format(self.path))
        except NoReverseMatch:
            # Admin might not be loaded.
            pass

        if settings.DEBUG and self.model.objects.published().count() == 0 and self.path == '/':
            # No pages in the database, present nice homepage.
            return self._intro_page()
        else:
            fallback = _get_fallback_language(self.language_code)
            if fallback:
                languages = (self.language_code, fallback)
                tried_msg = u" (language '{0}', fallback: '{1}')".format(*languages)
            else:
                tried_msg = u", language '{0}'".format(self.language_code)

            if self.path == '/':
                raise Http404(u"No published '{0}' found for the path '{1}'{2}. Use the 'Override URL' field to make sure a page can be found at the root of the site.".format(self.model.__name__, self.path, tried_msg))
            else:
                raise Http404(u"No published '{0}' found for the path '{1}'{2}.".format(self.model.__name__, self.path, tried_msg))

    def _intro_page(self):
        return TemplateResponse(self.request, "fluent_pages/intro_page.html", {
            'request': self.request,
            'site': Site.objects.get_current(),
        })

    def get_queryset(self):
        """
        Return the QuerySet used to find the pages.
        """
        # This can be limited or expanded in the future
        qs = self.model.objects.published(for_user=self.request.user)
        if self.prefetch_translations:
            qs = qs.prefetch_related('translations')
        return qs

    def get_object(self, path=None):
        """
        Return the UrlNode subclass object of the current page.
        """
        path = path or self.get_path()
        qs = self.get_queryset()

        return _try_languages(self.language_code, UrlNode.DoesNotExist,
            lambda lang: qs.get_for_path(path, language_code=lang)
        )

    def get_best_match_object(self, path=None):
        """
        Return the nearest UrlNode object for an URL path.
        """
        # Only check for nodes with custom urlpatterns
        path = path or self.get_path()
        qs = self.get_queryset().url_pattern_types()

        return _try_languages(self.language_code, UrlNode.DoesNotExist,
            lambda lang: qs.best_match_for_path(path, language_code=lang)
        )

    def get_plugin(self):
        """
        Return the rendering plugin for the current page object.
        """
        return self.object.plugin

    # -- Various resolver functions

    def _try_node(self):
        try:
            self.object = self.get_object()
        except self.model.DoesNotExist:
            return None

        # Before returning the response of an object,
        # check if the plugin overwrites the root url with a custom view.
        plugin = self.get_plugin()
        resolver = plugin.get_url_resolver()
        if resolver:
            try:
                match = resolver.resolve('/')
            except Resolver404:
                pass
            else:
                return self._call_url_view(plugin, '/', match)

        return self._call_node_view(plugin)

    def _call_node_view(self, plugin):
        """
        Call the regular view.
        """
        # Check that there wasn't a fetch in the fallback language,
        # perform some service for the user if this is the case.
        if _is_accidental_fallback(self.object, self.language_code):
            self.object.set_current_language(self.language_code)
            return HttpResponsePermanentRedirect(self.object.default_url)

        # Store the current page. This is used in the `app_reverse()` code,
        # and also avoids additional lookup in templatetags.
        # NOTE: django-fluent-blogs actually reads this variable too (should use CurrentPageMixin now)
        self.request._current_fluent_page = self.object
        prefill_parent_site(self.object)

        # Let page type plugin handle the request.
        response = plugin.get_response(self.request, self.object)
        if response is None:
            # Avoid automatic fallback to 404 page in this dispatcher.
            raise ValueError("The method '{0}.get_response()' didn't return an HttpResponse object.".format(plugin.__class__.__name__))

        return response

    def _try_node_redirect(self):
        # Check if the URLnode would be returned if the path did end with a slash.
        if self.path.endswith('/') or not settings.APPEND_SLASH:
            return None

        try:
            self.object = self.get_object(self.path + '/')
        except self.model.DoesNotExist:
            return None
        else:
            return HttpResponseRedirect(self.request.path + '/')

    def _try_appnode(self):
        try:
            self.object = self.get_best_match_object()
        except self.model.DoesNotExist:
            return None

        # See if the application can resolve URLs
        plugin = self.get_plugin()
        resolver = plugin.get_url_resolver()
        if not resolver:
            return None

        # Strip the full CMS url from the path_info,
        # so the remainder can be passed to the URL resolver of the app.
        # Using default_url instead of get_absolute_url() to avoid ABSOLUTE_URL_OVERRIDES issues (e.g. adding a hostname)
        urlnode_path = self.object.default_url.rstrip('/')
        sub_path = self.request.path[len(urlnode_path):]  # path_info starts at script_prefix, path starts at root.

        try:
            match = resolver.resolve(sub_path)
        except Resolver404:
            # Again implement APPEND_SLASH behavior here,
            # since the middleware is circumvented by the URLconf regex.
            if not sub_path.endswith('/') and settings.APPEND_SLASH:
                try:
                    match = resolver.resolve(sub_path + '/')
                except Resolver404:
                    return None
                else:
                    return HttpResponseRedirect(self.request.path + '/')
            return None
        else:
            # Call application view.
            return self._call_url_view(plugin, sub_path, match)

    def _call_url_view(self, plugin, sub_path, match):
        """
        Call the extra URLpattern view.
        """
        # Check that there wasn't a fetch in the fallback language,
        # perform some service for the user if this is the case.
        if _is_accidental_fallback(self.object, self.language_code):
            self.object.set_current_language(self.language_code)
            return HttpResponsePermanentRedirect(self.object.default_url.rstrip('/') + sub_path)

        # Avoid additional lookup in templatetags
        self.request._current_fluent_page = self.object
        prefill_parent_site(self.object)

        # Get view response
        response = plugin.get_view_response(self.request, self.object, match.func, match.args, match.kwargs)
        if response is None:
            raise RuntimeError("The view '{0}' didn't return an HttpResponse object.".format(match.url_name))

        return response

    def _try_append_slash_redirect(self):
        if self.path.endswith('/') or not settings.APPEND_SLASH:
            return None

        urlconf = getattr(self.request, 'urlconf', None)
        try:
            match = resolve(self.request.path_info + '/', urlconf)
        except Resolver404:
            return None

        if not self._is_own_view(match):
            if settings.DEBUG and self.request.method == 'POST':
                raise RuntimeError((""
                    "You called this URL via POST, but the URL doesn't end "
                    "in a slash and you have APPEND_SLASH set. Django can't "
                    "redirect to the slash URL while maintaining POST data. "
                    "Change your form to point to %s%s (note the trailing "
                    "slash), or set APPEND_SLASH=False in your Django "
                    "settings.") % (self.request.path, '/'))
            return HttpResponseRedirect(self.request.path + '/')
        return None

    def _is_own_view(self, match):
        return match.app_name == 'fluent_pages' \
            or match.url_name in ('fluent-page', 'fluent-page-url')


class CmsPageAdminRedirect(GetPathMixin, RedirectView):
    """
    A view which redirects to the admin.
    """
    permanent = False

    def get_redirect_url(self, **kwargs):
        # Avoid importing the admin too early via the URLconf.
        # This gives errors when 'fluent_pages' is not in INSTALLED_APPS yet.
        from fluent_pages.adminui.utils import get_page_admin_url

        path = self.get_path()
        language_code = self.get_language()
        qs = UrlNode.objects.non_polymorphic().published(for_user=self.request.user)

        try:
            page = _try_languages(language_code, UrlNode.DoesNotExist,
                lambda lang: qs.get_for_path(path, language_code=lang)
            )
            url = get_page_admin_url(page)
        except UrlNode.DoesNotExist:
            # Back to page without @admin, display the error there.
            url = re.sub('@[^@]+/?$', '', self.request.path)

        return self.request.build_absolute_uri(url)


def _try_languages(language_code, exception_class, func):
    """
    Try running the same code with different languages.
    """
    try:
        return func(language_code)
    except exception_class:
        # see if there is a fallback language
        fallback = _get_fallback_language(language_code)
        if not fallback:
            # There is not another possible attempt, raise.
            raise

    try:
        obj = func(fallback)
    except exception_class as e:
        raise exception_class(u"{0}\nTried languages: {1}, {2}".format(str(e), language_code, fallback), e)

    # NOTE: it could happen that objects are resolved using their fallback language,
    # but the actual translation also exists. This is handled in _get_node() above.
    setattr(obj, "_fetched_in_fallback_language", True)
    return obj


def _is_accidental_fallback(obj, requested_language):
    # The object was resolved via the fallback language, but it has an official URL in the translated language.
    # Either _try_languages() can raise an exception, or we could perform a redirect on the users behalf.
    return getattr(obj, '_fetched_in_fallback_language', False) \
       and obj.has_translation(requested_language)


def _get_fallback_language(language_code):
    """
    Whether to try the default language.
    """
    # Re-use django-parler logic, which takes `hide_untranslated` into account.
    # Choices = (language, fallback) or (language,)
    choices = appsettings.FLUENT_PAGES_LANGUAGES.get_active_choices(language_code)
    if len(choices) <= 1:
        return None
    else:
        return choices[-1]
