"""
Definition of the plugin.
"""
from django import forms
from ecms.extensions import EcmsPlugin, plugin_pool, CmsPageItemForm
from .models import CmsTextItem   # absolute import failed?


class CmsTextItemForm(CmsPageItemForm):
    class Media:
        js = ('ecms_plugins/text/text_admin.js',)
        css = {'screen': ('ecms_plugins/text/text_admin.css',)}


class EcmsTextPlugin(EcmsPlugin):
    model = CmsTextItem
    admin_form = CmsTextItemForm
    admin_form_template = "admin/ecms_plugins/text/admin_form.html"


plugin_pool.register(EcmsTextPlugin)
