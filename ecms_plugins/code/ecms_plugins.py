"""
Definition of the plugin.
"""
from ecms.extensions import EcmsPlugin, plugin_pool
from .models import CodeItem
from . import appsettings, backend


class EcmsCodePlugin(EcmsPlugin):
    model = CodeItem
    category = 'programming'
    admin_form_template = "admin/ecms_plugins/code/admin_form.html"

    class Media:
        css = {'screen': ('ecms_plugins/code/code_admin.css',)}

    @classmethod
    def render(cls, instance):
        # Style is not stored in the model,
        # it needs to be a side-wide setting (maybe even in the theme)
        return backend.render_code(instance, style_name=appsettings.ECMS_CODE_DEFAULT_STYLE)


plugin_pool.register(EcmsCodePlugin)
