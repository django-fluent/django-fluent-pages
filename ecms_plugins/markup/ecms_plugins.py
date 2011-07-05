"""
Definition of the plugin.
"""
from __future__ import absolute_import
from ecms.extensions import EcmsPlugin, plugin_pool, render_error
from ecms_plugins.markup.models import MarkupItem, MarkupItemForm
from ecms_plugins.markup import backend


class EcmsMarkupPlugin(EcmsPlugin):
    model = MarkupItem
    admin_form = MarkupItemForm
    #admin_form_template = "admin/ecms_plugins/markup/admin_form.html"

    @classmethod
    def render(cls, instance):
        try:
            html = backend.render_text(instance.text, instance.language)
        except Exception, e:
            html = render_error(e)

        # Included in a DIV, so the next item will be displayed below.
        return '<div class="markup">' + html + '</div>\n'


plugin_pool.register(EcmsMarkupPlugin)
