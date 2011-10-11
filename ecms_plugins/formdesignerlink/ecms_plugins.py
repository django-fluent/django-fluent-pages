"""
Form designer link plugin.

This plugin displays a form at the page, that was created with form_designer.
To customize the output, configure the ``django-form-designer`` application via the settings file.
For example, use:

 * ``FORM_DESIGNER_DEFAULT_FORM_TEMPLATE`` or ``FORM_TEMPLATES`` to control the form output (e.g. render it with ``django-uni-form``).
 * ``FORM_DESIGNER_FIELD_CLASSES`` to define which field types are allowed.
 * ``FORM_DESIGNER_WIDGET_CLASSES`` to define which widgets are allowed.
"""
from __future__ import absolute_import
from form_designer import settings as form_designer_settings
from form_designer.views import process_form
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.formdesignerlink.models import FormDesignerLink


class EcmsFormDesignerLinkPlugin(EcmsPlugin):
    model = FormDesignerLink
    category = 'interactivity'

    @classmethod
    def get_render_template(cls, instance, request, **kwargs):
        return instance.form_definition.form_template_name or cls.render_template or form_designer_settings.DEFAULT_FORM_TEMPLATE

    @classmethod
    def get_context(cls, instance, request, **kwargs):
        context = {}
        # The process_form() function is designed with Django CMS in mind,
        # and responds to both the GET and POST request.
        return process_form(request, instance.form_definition, context, is_cms_plugin=True)


plugin_pool.register(EcmsFormDesignerLinkPlugin)
