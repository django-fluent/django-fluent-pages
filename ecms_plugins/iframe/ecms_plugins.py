"""
Plugin to add an ``<iframe>`` to the page.
"""
from __future__ import absolute_import
from django.utils.html import escape
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.iframe.models import IframeItem


class IframePlugin(EcmsPlugin):
    model = IframeItem
    category = 'advanced'

    @classmethod
    def render(cls, instance, request, **kwargs):
        return u'<iframe class="iframe" src="{src}" width="{width}" height="{height}"></iframe>'.format(
            src=escape(instance.src),
            width=instance.width,
            height=instance.height
        )


plugin_pool.register(IframePlugin)
