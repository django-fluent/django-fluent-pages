"""
Definition of the plugin.
"""
from ecms.extensions import EcmsPlugin, plugin_pool
from .models import CodeItem


class EcmsCodePlugin(EcmsPlugin):
    model = CodeItem

    class Media:
        css = {'screen': ('ecms_plugins/code/code_admin.css',)}

plugin_pool.register(EcmsCodePlugin)
