"""
Definition of the plugin.
"""
from ecms.extensions import EcmsPlugin, plugin_pool
from .models import CmsTextItem   # absolute import failed?


class EcmsTextPlugin(EcmsPlugin):
    model = CmsTextItem
    admin_form_template = "admin/ecms_plugins/text/admin_form.html"


plugin_pool.register(EcmsTextPlugin)
