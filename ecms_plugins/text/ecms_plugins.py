"""
Definition of the plugin.
"""
from __future__ import absolute_import
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.text.models import CmsTextItem


class EcmsTextPlugin(EcmsPlugin):
    model = CmsTextItem
    admin_form_template = "admin/ecms_plugins/text/admin_form.html"

    class Media:
        js = ('ecms_plugins/text/text_admin.js',)
        css = {'screen': ('ecms_plugins/text/text_admin.css',)}


plugin_pool.register(EcmsTextPlugin)
