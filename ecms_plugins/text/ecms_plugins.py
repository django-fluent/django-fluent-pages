"""
Definition of the plugin.
"""
from __future__ import absolute_import
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.text.models import CmsTextItem   # absolute import failed?


class EcmsTextPlugin(EcmsPlugin):
    model = CmsTextItem
    admin_form_template = "admin/ecms_plugins/text/admin_form.html"

    class Media:
        js = ('ecms_plugins/text/text_admin.js',)
        css = {'screen': ('ecms_plugins/text/text_admin.css',)}

    @classmethod
    def render(cls, instance, request, **kwargs):
        # Included in a DIV, so the next item will be displayed below.
        return '<div class="text">' + instance.text + '</div>\n'


plugin_pool.register(EcmsTextPlugin)
