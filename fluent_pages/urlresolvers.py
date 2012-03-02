from django.core.urlresolvers import NoReverseMatch, reverse
from fluent_pages.extensions import page_type_pool
from fluent_pages.models.db import UrlNode


class MultipleReverseMatch(NoReverseMatch):
    pass


class PageTypeNotMounted(NoReverseMatch):
    pass


def mixed_reverse(viewname, args=None, kwargs=None, current_app=None, current_page=None, multiple=False):
    """
    Attempt to reverse a normal URLconf URL, revert to app_reverse() on errors.
    """
    try:
        return reverse(viewname, args=args, kwargs=kwargs, current_app=current_app)
    except NoReverseMatch:
        return app_reverse(viewname, args=args, kwargs=kwargs, multiple=multiple, current_page=current_page)


def app_reverse(viewname, args=None, kwargs=None, multiple=False, current_page=None):
    """
    Locate an URL which is located under a page type.
    """
    # Do a reverse on every possible page type that supports URLs
    args = args or []
    kwargs = kwargs or {}
    plugin, url_end = _find_plugin_reverse(viewname, args, kwargs)

    # TODO: allow caching of the results

    # Find where the URL is currently hosted.
    pages = UrlNode.objects.published().non_polymorphic().instance_of(plugin.model)

    if len(pages) > 1 and not multiple:
        # Multiple results available.
        # If there is a current page, it can be used as base URL, otherwise bail out.
        if current_page and current_page.plugin is plugin:
            for page in pages:
                if page.pk == current_page.pk:
                    return current_page.get_absolute_url() + url_end

        raise MultipleReverseMatch("Reverse for application URL '{0}' found, but multiple root nodes available: {1}".format(
            viewname, ', '.join(page.get_absolute_url() for page in pages)
        ))
    elif not pages:
        raise PageTypeNotMounted("Reverse for application URL '{0}' not found, page type '{1}' is not added in the page tree.".format(plugin.type_name))

    # Return URL with page prefix.
    if multiple:
        return (page.get_absolute_url() + url_end for page in pages)
    else:
        return pages[0].get_absolute_url() + url_end


def _find_plugin_reverse(viewname, args, kwargs):
    plugins = page_type_pool.get_url_pattern_plugins()
    for plugin in plugins:
        try:
            url_end = plugin.get_url_resolver().reverse(viewname, *args, **kwargs)
            return plugin, url_end
        except NoReverseMatch:
            pass
    else:
        raise NoReverseMatch("Reverse for application URL '%s' with arguments '%s' and keyword "
                             "arguments '%s' not found." % (viewname, args, kwargs))
