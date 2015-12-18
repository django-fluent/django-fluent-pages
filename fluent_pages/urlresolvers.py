"""
URL Resolving for dynamically added pages.
"""
from django.utils.functional import lazy
from future.builtins import str
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.translation import get_language

# Several imports in this file are placed inline, to avoid loading the models too early.
# Because fluent_pages.models creates a QuerySet, all all apps will be imported.
# By reducing the import statements here, other apps (e.g. django-fluent-blogs) can already import this module safely.
# Also, note that mixed_reverse_lazy() could be used from the Django settings file.

__all__ = (
    'MultipleReverseMatch',
    'PageTypeNotMounted',
    'mixed_reverse',
    'mixed_reverse_lazy',
    'app_reverse',
    'app_reverse_lazy',
    'clear_app_reverse_cache',
)


class MultipleReverseMatch(NoReverseMatch):
    """
    Raised when an :func:`app_reverse` call returns multiple possible matches.
    """
    pass


class PageTypeNotMounted(NoReverseMatch):
    """
    Raised when the :func:`app_reverse` function can't find the required plugin
    in the page tree.
    """
    pass


def mixed_reverse(viewname, args=None, kwargs=None, current_app=None, current_page=None, language_code=None, multiple=False, ignore_multiple=False):
    """
    Attempt to reverse a normal URLconf URL, revert to :func:`app_reverse` on errors.
    """
    try:
        return reverse(viewname, args=args, kwargs=kwargs, current_app=current_app)
    except NoReverseMatch:
        return app_reverse(viewname, args=args, kwargs=kwargs, multiple=multiple, ignore_multiple=ignore_multiple, current_page=current_page, language_code=language_code)


def app_reverse(viewname, args=None, kwargs=None, multiple=False, ignore_multiple=False, current_page=None, language_code=None):
    """
    Locate an URL which is located under a page type.
    """
    # Do a reverse on every possible page type that supports URLs
    args = args or []
    kwargs = kwargs or {}

    # Find the plugin
    # TODO: allow more caching of the results
    plugin, url_end = _find_plugin_reverse(viewname, args, kwargs)
    pages = _get_pages_of_type(plugin.model, language_code=language_code)

    if len(pages) > 1 and not (multiple or ignore_multiple):
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
        raise PageTypeNotMounted("Reverse for application URL '{0}' is not available, a '{1}' page needs to be added to the page tree.".format(viewname, str(plugin.verbose_name)))

    # Return URL with page prefix.
    if multiple:
        return (page.get_absolute_url() + url_end for page in pages)
    else:
        # single result, or ignoring multiple results.
        return pages[0].get_absolute_url() + url_end


mixed_reverse_lazy = lazy(mixed_reverse, str)
app_reverse_lazy = lazy(app_reverse, str)


def _find_plugin_reverse(viewname, args, kwargs):
    from fluent_pages.extensions import page_type_pool
    plugins = page_type_pool.get_url_pattern_plugins()
    for plugin in plugins:
        try:
            url_end = plugin.get_url_resolver().reverse(viewname, *args, **kwargs)
            return plugin, url_end
        except NoReverseMatch:
            pass
    else:
        raise NoReverseMatch(
            "Reverse for application URL '{0}' with arguments '{1}' and keyword arguments '{2}' not found.\n"
            "Searched in URLconf and installed page type plugins ({3}) for URLs.".format(
                viewname, args, kwargs, ', '.join(x.__class__.__name__ for x in page_type_pool.get_plugins()) or "none"
        ))


def _get_pages_of_type(model, language_code=None):
    """
    Find where a given model is hosted.
    """
    from django.conf import settings
    from django.core.cache import cache
    from fluent_pages.models.db import UrlNode
    if language_code is None:
        language_code = get_language()

    cachekey = 'fluent_pages.instance_of.{0}.{1}'.format(model.__name__, settings.SITE_ID)
    pages = cache.get(cachekey)
    if not pages:
        pages = UrlNode.objects.published().non_polymorphic().instance_of(model).only(
            'parent', 'lft',  # add fields read by MPTT, otherwise .only() causes infinite loop in django-mptt 0.5.2
            'id'              # for Django 1.3
        )

        # Short cache time of 1 hour, take into account that the publication date can affect this value.
        pages = list(pages)   # Make output consistent with non-cached version
        cache.set(cachekey, pages, 3600)

    # Return in desired language
    # This is effectively what qs.language(..) does
    result = []
    for page in pages:
        page.set_current_language(language_code)

        # Filter the pages that are not available in the given language code.
        # Currently not splitting the cached query, makes invalidation much harder.
        if page.has_translation(language_code) or page.has_translation(page.get_fallback_language()):
            result.append(page)

    return result


def clear_app_reverse_cache():
    """
    Clear the cache for the :func:`app_reverse` function.
    This only has to be called when doing bulk update/delete actions that circumvent the individual model classes.
    """
    from django.core.cache import cache
    from fluent_pages.extensions import page_type_pool
    for model in page_type_pool.get_model_classes():
        cache.delete('fluent_pages.instance_of.{0}'.format(model.__name__))
