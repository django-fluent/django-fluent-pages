"""
Definition of the plugin.
"""
from ecms.extensions import EcmsPlugin, plugin_pool
from .models import CmsTextItem   # absolute import failed?


class EcmsTextPlugin(EcmsPlugin):
    model = CmsTextItem
    admin_form_template = "admin/ecms_plugins/text/admin_form.html"

    class Media:
        js = ('ecms_plugins/text/text_admin.js',)
        css = {'screen': ('ecms_plugins/text/text_admin.css',)}


plugin_pool.register(EcmsTextPlugin)
