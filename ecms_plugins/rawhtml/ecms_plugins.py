from ecms.extensions import EcmsPlugin, plugin_pool
from .models import RawHtmlItem

class RawHtmlPlugin(EcmsPlugin):
    """
    Plugin for rendering raw HTML output.
    This can be used to insert embed codes in a webpage,
    for example for Google Docs, YouTube or SlideShare.
    """
    model = RawHtmlItem
    category = 'advanced'
    admin_form_template = "admin/ecms_plugins/rawhtml/admin_form.html"

    class Media:
        css = {'screen': ('ecms_plugins/rawhtml/rawhtml_admin.css',)}

    @classmethod
    def render(cls, instance, request, **kwargs):
        return instance.html


plugin_pool.register(RawHtmlPlugin)
