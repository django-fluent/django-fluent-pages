"""
Plugin for rendering Gist snippets, hosted by Github.
"""
from ecms.extensions import EcmsPlugin, plugin_pool
from .models import GistItem
import urllib2

class GistPlugin(EcmsPlugin):
    model = GistItem
    category = 'programming'

    @classmethod
    def render(cls, instance):
        url = 'http://gist.github.com/%s.js' % int(instance.gist_id)
        if instance.filename:
            url += '?file=' + urllib2.quote(instance.filename)

        return '<script src="%s"></script>' % url


plugin_pool.register(GistPlugin)
