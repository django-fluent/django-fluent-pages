from __future__ import absolute_import
from django.conf import settings
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.disquswidgets.models import CmsDisqusCommentsItem


class EcmsDisqusCommentsPlugin(EcmsPlugin):
    model = CmsDisqusCommentsItem
    category = 'interactivity'
    render_template = "ecms_plugins/disquswidgets/comments.html"

    @classmethod
    def get_context(cls, instance, request, **kwargs):
        return {
            'instance': instance,
            'DISQUS_WEBSITE_SHORTNAME': settings.DISQUS_WEBSITE_SHORTNAME,
            'DEBUG': settings.DEBUG,
        }


plugin_pool.register(EcmsDisqusCommentsPlugin)
