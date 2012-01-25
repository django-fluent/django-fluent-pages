"""
The view to display CMS content.
"""
from django.conf import settings
from django.core.urlresolvers import Resolver404, reverse
from django.http import Http404, HttpResponseRedirect
from django.views.generic.base import View
from fluent_pages.models import UrlNode
from fluent_pages.admin.utils import get_page_admin_url
from fluent_pages.extensions import page_type_pool
from django.views.generic import RedirectView
import re


class CmsPageDispatcher(View):
    """
    The view which displays a CMS page.
    This is not a ``DetailsView`` by design, as the rendering is redirected to the page type plugin.
    """
    model = UrlNode

    def get(self, request, **kwargs):
        """Display the page in a GET request."""
        self.path = self.get_path()

        # Since this view acts as a catch-all, give better error messages
        # when mistyping an admin URL. Don't mention anything about CMS pages.
        if self.path.startswith(reverse('admin:index', prefix='/')):
            raise Http404("No admin page found at '{0}'\n(raised by fluent_pages catch-all).".format(self.path))

        for func in (self._get_node, self._get_urlnode_redirect, self._get_appnode):
            response = func()
            if response:
                return response

        raise Http404("No published '{0}' found for the path: '{1}'".format(self.model.__name__, self.path))

    def post(self, request, **kwargs):
        """Allow POST requests (for forms) to the page."""
        return self.get(request, **kwargs)

    def get_path(self):
        if self.kwargs.has_key('path'):
            # Starting slash is removed by URLconf, restore it.
            return '/' + (self.kwargs['path'] or '')
        else:
            # Path from current script prefix
            return self.request.path_info

    def get_queryset(self):
        """
        Return the QuerySet used to find the pages.
        """
        # This can be limited or expanded in the future
        return self.model.objects.published()

    def get_object(self, path=None):
        """
        Return the UrlNode subclass object of the current page.
        """
        path = path or self.get_path()
        return self.get_queryset().get_for_path(path)

    def get_best_match_object(self, path=None):
        path = path or self.get_path()
        return self.get_queryset().best_match_for_path(path)

    def get_plugin(self):
        """Return the rendering plugin for the current page object."""
        return page_type_pool.get_plugin_by_model(self.object.__class__)


    # -- Various

    def _get_node(self):
        try:
            self.object = self.get_object()
        except self.model.DoesNotExist:
            return None

        # Before returning the response of an object,
        # check if the root url is overlapped by an application.
        plugin = self.get_plugin()
        resolver = plugin.get_url_resolver()
        if resolver:
            try:
                match = resolver.resolve('/')
            except Resolver404:
                pass
            else:
                return match.func(self.request, *match.args, **match.kwargs)

        response = plugin.get_response(self.request, self.object)
        if response is None:
            # Avoid automatic fallback to 404 page in this dispatcher.
            raise RuntimeError("No response received from plugin '{0}'".format(plugin.__class__.__name__))
        return response


    def _get_urlnode_redirect(self):
        if self.path.endswith('/') or not settings.APPEND_SLASH:
            return None

        try:
            self.object = self.get_object(self.path + '/')
        except self.model.DoesNotExist:
            return None
        else:
            return HttpResponseRedirect(self.request.path + '/')


    def _get_appnode(self):
        try:
            self.object = self.get_best_match_object()
        except self.model.DoesNotExist:
            return None

        # See if the application can resolve URLs
        resolver = self.get_plugin().get_url_resolver()
        if not resolver:
            return None

        urlnode_path = self.object._cached_url.rstrip('/')
        sub_path = self.request.path_info[len(urlnode_path):]  # path_info starts at script_prefix

        try:
            match = resolver.resolve(sub_path)
        except Resolver404:
            if not sub_path.endswith('/') and settings.APPEND_SLASH:
                try:
                    match = resolver.resolve(sub_path + '/')
                except Resolver404:
                    return None
                else:
                    return HttpResponseRedirect(self.request.path + '/')
            return None
        else:
            response = match.func(self.request, *match.args, **match.kwargs)
            if response is None:
                raise RuntimeError("No response received from view '{0}'".format(match.url_name))
            return response


class CmsPageAdminRedirect(RedirectView):
    """
    A view which redirects to the admin.
    """
    def get_redirect_url(self, **kwargs):
        path = self.kwargs.get('path', self.request.path) or ''
        try:
            page = UrlNode.objects.non_polymorphic().get_for_path(path)
            return get_page_admin_url(page)
        except UrlNode.DoesNotExist:
            # Back to page without @admin, display the error there.
            return '/' + re.sub('@[^@]+/?$', '', path)
