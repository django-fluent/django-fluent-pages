"""
Definition of the plugin.
"""
from __future__ import absolute_import
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.markup.models import MarkupItem, MarkupItemForm


class EcmsMarkupPlugin(EcmsPlugin):
    model = MarkupItem
    admin_form = MarkupItemForm
    #admin_form_template = "admin/ecms_plugins/markup/admin_form.html"

plugin_pool.register(EcmsMarkupPlugin)
