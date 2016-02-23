"""
Mixins to simplify creating URLpattern views in custom page pages.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from fluent_pages.urlresolvers import mixed_reverse
from parler.views import ViewUrlMixin


class CurrentPageMixin(ViewUrlMixin):
    """
    Access the current page.
    This can be used for views which are defined as page type views
    in :attr:`PageTypePlugin.urls <fluent_pages.extensions.PageTypePlugin.urls>`.

    The template context will have the same variables as the regular page templates would have,
    which are:
    * ``page``
    * ``site``
    * :ref:`FLUENT_PAGES_BASE_TEMPLATE`
    """

    def get_current_page(self):
        """
        Return the current page.
        """
        return getattr(self.request, '_current_fluent_page', None)

    def get_context_data(self, **kwargs):
        """
        Add the plugin context to the template.
        """
        context = super(CurrentPageMixin, self).get_context_data(**kwargs)
        page = self.get_current_page()

        # Expose the same context data as PageTypePlugin.get_context()
        # so make it work consistently between CMS pages and mounted app pages.
        # Delay the 'site' query until the variable is read, and cache it afterwards.
        if page is not None:
            context.update(page.plugin.get_context(self.request, page))

            # Improve the integration of django-staff-toolbar, if used.
            # However, avoid being too disruptive, in case the view exposes an object themselves.
            if 'staff_toolbar' in settings.INSTALLED_APPS:
                if getattr(self, 'object', None) is None \
                        and 'object' not in context \
                        and not hasattr(self, 'get_staff_object') \
                        and not hasattr(self.request, 'staff_object'):
                    self.request.staff_object = page

        return context

    def get_view_url(self):
        """
        When using the :attr:`ViewUrlMixin.view_url_name <parler.views.ViewUrlMixin.view_url_name>` feature of *django-parler*,
        this makes sure that mounted pages are also supported.

        It uses :func:`fluent_pages.urlresolvers.mixed_reverse` function to resolve the :attr:`view_url_name`.
        """
        # This method is used by the ``get_translated_url`` template tag of django-parler
        if self.view_url_name:
            return mixed_reverse(self.view_url_name, args=self.args, kwargs=self.kwargs, current_page=self.get_current_page())
        else:
            return super(CurrentPageMixin, self).get_view_url()


class CurrentPageTemplateMixin(CurrentPageMixin):
    """
    Automaticaly reuse the template of the current page for the URL pattern view.
    """

    def get_template_names(self):
        """
        Auto-include the template of the CMS page.
        """
        page = self.get_current_page()
        if page is not None:
            extra_template = page.plugin.get_render_template(self.request, page)
        else:
            extra_template = None

        names = []
        try:
            # This call will likely resolve into:
            # * TemplateResponseMixin (reads template_name)
            # * SingleObjectTemplateResponseMixin (uses model name)
            names = super(CurrentPageMixin, self).get_template_names()
        except ImproperlyConfigured:
            # No problem, if the plugin offered a template name that will be used.
            if extra_template:
                names.append(extra_template)
            else:
                # Really need to define `template_name` yourself.
                raise
        else:
            # There are already template choices,
            # add the page templates as last choice (if the model-specific page does not exist).
            if extra_template:
                names.append(extra_template)

        return names
