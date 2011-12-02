"""
Google apps widgets for your site.
"""
from __future__ import absolute_import
from django.utils.html import escape
from django.utils.http import urlquote
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.googledocsviewer.models import GoogleDocsViewerItem


class GoogleDocsViewerPlugin(EcmsPlugin):
    """
    Plugin to add a Google Docs viewer to the page.
    This can be used to display a PDF file inline.

    Note then when using the Google Docs viewer on your site,
    Google assumes you agree with the Terms of Service,
    see: https://docs.google.com/viewer/TOS
    """
    model = GoogleDocsViewerItem
    category = 'online-services'

    @classmethod
    def render(cls, instance, request, **kwargs):
        url = 'http://docs.google.com/viewer?url={url}&embedded=true'.format(url=urlquote(instance.url, ''))
        return u'<iframe class="googledocsviewer" src="{src}" width="{width}" height="{height}"></iframe>'.format(
            src=escape(url),
            width=instance.width,
            height=instance.height
        )


plugin_pool.register(GoogleDocsViewerPlugin)
