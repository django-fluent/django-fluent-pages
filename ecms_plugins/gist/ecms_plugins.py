"""
Plugin for rendering Gist snippets, hosted by Github.
"""
from __future__ import absolute_import
from django.utils.http import urlquote
from ecms.extensions import EcmsPlugin, plugin_pool
from ecms_plugins.gist.models import GistItem


class GistPlugin(EcmsPlugin):
    model = GistItem
    category = 'programming'

    @classmethod
    def render(cls, instance, request, **kwargs):
        url = u'http://gist.github.com/{0}.js'.format(instance.gist_id)
        if instance.filename:
            url += u'?file={0}'.format(urlquote(instance.filename))

        return u'<script src="{0}"></script>'.format(url)


plugin_pool.register(GistPlugin)
