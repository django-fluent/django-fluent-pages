"""
Admin classes to create page.
Everything can be imported from ``__init__.py``.
"""
from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import get_template
from fluent_contents.admin import PlaceholderEditorAdmin
from fluent_contents.models import ContentItem
from fluent_pages.adminui import HtmlPageAdmin
from fluent_contents.analyzer import get_template_placeholder_data
from fluent_contents.extensions import plugin_pool, PluginNotFound


class FluentContentsPageAdmin(PlaceholderEditorAdmin, HtmlPageAdmin):
    """
    This admin is a small binding between the pagetypes of *django-fluent-pages*
    and page contents of *django-fluent-contents*.

    Use ``{% extends base_change_form_template %}`` in your page template, and it will all work properly.
    """
    # Make sure all templates use our integration template as base.
    base_change_form_template = "admin/fluent_pages/integration/fluent_contents/base_change_form.html"

    #: A fixed defined placeholder layout, which can be defined statically.
    #: This should be a list of :class:`~fluent_contents.models.PlaceholderData` objects.
    placeholder_layout = None

    #: A fixed template, from which the placeholder data can be read.
    #: The :attr:`placeholder_layout` will be read automatically from the template.
    placeholder_layout_template = None

    #: A static list of all allowed plugin names.
    #: This is read by :func:`get_all_allowed_plugins`
    all_allowed_plugins = None

    def get_placeholder_data(self, request, obj=None):
        """
        Read the placeholder data to display in the template.
        This reads :attr:`placeholder_layout` and :attr:`placeholder_layout_template`.
        It can be overwritten to return the layout depending on the page or request.

        Tip: if the object is given, this could read ``obj.plugin.get_render_template(request, obj)`` too.
        """
        # This information is "magically" picked up in the template to create the tabs.
        # Some details about the inner workings of django-fluent-contents:
        # - the PlaceholderEditorInline reads this to construct the formset.
        # - the formset data is exposed to the template.
        # - the tabs are created based on the formset data.
        #
        if self.placeholder_layout:
            # Assume a list of `PlaceholderData` objects.
            return self.placeholder_layout
        elif self.placeholder_layout_template:
            # Read the placeholder data from the template once.
            template = get_template(self.placeholder_layout_template)
            self.placeholder_layout = get_template_placeholder_data(template)
            return self.placeholder_layout
        else:
            # Similar to PlaceholderEditorAdmin.get_placeholder_data(),
            # raise an exception to indicate the class is not properly used.
            raise ImproperlyConfigured(
                "The '{0}' subclass should define a static 'placeholder_layout', "
                "a 'placeholder_layout_template', "
                "or overwrite get_placeholder_data().".format(self.__class__.__name__)
            )

    def get_all_allowed_plugins(self):
        """
        By default, all plugins are allowed, unless a placeholder puts a limit on this.
        The page will load much faster if the plugin types are limited globally here.
        """
        if self.all_allowed_plugins:
            # Limit the globally available plugins,
            # using the statically defined list.
            try:
                return plugin_pool.get_plugins_by_name(*self.all_allowed_plugins)
            except PluginNotFound as e:
                raise PluginNotFound(str(e) + " Update the plugin list of the {0}.all_allowed_plugins setting.".format(self.__class__.__name__))
        elif self.placeholder_layout_template:
            # This page is edited with a fixed template.
            # Extract all slot names from the template, and base the list of plugins on that.
            # Note that this actually parses the template, but it will be cached for production environments.
            template = get_template(self.placeholder_layout_template)
            slots = [placeholder.slot for placeholder in get_template_placeholder_data(template)]

            # Resolve all plugins.
            plugins = []
            for slot in slots:
                plugins.extend(plugin_pool.get_allowed_plugins(slot))
            plugins = list(set(plugins))

            # The list of names can be stored statically because it won't change anyway.
            # Otherwise it would be read at least 3 times in a request,
            # from the admin get_inline_instances(), get_formset() and
            if not settings.DEBUG:
                self.all_allowed_plugins = [plugin.name for plugin in plugins]

            return plugins
        else:
            # Accepts all plugins by default
            return super(FluentContentsPageAdmin, self).get_all_allowed_plugins()

    def get_translation_objects(self, request, language_code, obj=None, inlines=True):
        """
        Make sure the translated ContentItem objects are also deleted when a translation is removed.
        """
        for qs in super(FluentContentsPageAdmin, self).get_translation_objects(request, language_code, obj=obj, inlines=inlines):
            yield qs

        if obj is not None and inlines:
            yield ContentItem.objects.parent(obj, limit_parent_language=False).filter(language_code=language_code)
