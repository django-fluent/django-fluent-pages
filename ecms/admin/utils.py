"""
Extra utilities related to the admin
"""
from django.core import urlresolvers
from ecms.extensions import PLUGIN_CATEGORIES


def get_page_admin_url(page):
    """
    Return the admin URL for a page.
    """
    return urlresolvers.reverse('admin:ecms_cmsobject_change', args=(page.id,))


def get_pageitem_choices(plugins):
    """
    Return a tuple of plugin model choices, suitable for a select field.
    """
    categories = get_pageitem_categories(plugins)
    choices = []
    for category, items in categories.iteritems():
        if items:
            plugin_tuples = tuple((plugin.model.__name__, plugin.verbose_name) for plugin in items)
            if category:
                choices.append((PLUGIN_CATEGORIES[category], plugin_tuples))
            else:
                choices += plugin_tuples

    return choices


def get_pageitem_categories(plugins):
    """
    Split a list of plugins into a dictionary of categories
    """
    plugins = sorted(plugins, key=lambda p: p.verbose_name)
    categories = dict((c, []) for c in PLUGIN_CATEGORIES)

    for plugin in plugins:
        if not categories.has_key(plugin.category):
            categories['unknown'].append(plugin)
        else:
            categories[plugin.category].append(plugin)

    categories = dict(i for i in categories.iteritems() if i[1])
    return categories