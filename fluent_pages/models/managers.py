"""
The manager class for the CMS models
"""
import django
from future.builtins import range
from django.conf import settings
from django.db.models.query_utils import Q
from django.utils.translation import get_language
from django.utils.timezone import now

from parler import is_multilingual_project
from parler.managers import TranslatableQuerySet, TranslatableManager
from polymorphic_tree.managers import PolymorphicMPTTModelManager, PolymorphicMPTTQuerySet
from fluent_pages import appsettings
from .utils import DecoratingQuerySet


class UrlNodeQuerySet(TranslatableQuerySet, DecoratingQuerySet, PolymorphicMPTTQuerySet):
    """
    Queryset methods for UrlNode objects.
    """

    def __init__(self, *args, **kwargs):
        super(UrlNodeQuerySet, self).__init__(*args, **kwargs)
        self._parent_site = None

    def _clone(self, *args, **kwargs):
        c = super(UrlNodeQuerySet, self)._clone(*args, **kwargs)
        c._parent_site = self._parent_site
        return c

    def active_translations(self, language_code=None, **translated_fields):
        # overwritten to honor our settings instead of the django-parler defaults
        language_codes = appsettings.FLUENT_PAGES_LANGUAGES.get_active_choices(language_code)
        return self.translated(*language_codes, **translated_fields)

    def get_for_path(self, path, language_code=None):
        """
        Return the UrlNode for the given path.
        The path is expected to start with an initial slash.

        Raises UrlNode.DoesNotExist when the item is not found.

        .. versionchanged:: 0.9 This filter only returns the pages of the current site.
        """
        if language_code is None:
            language_code = self._language or get_language()

        # Don't normalize slashes, expect the URLs to be sane.
        try:
            obj = self._single_site().get(translations___cached_url=path, translations__language_code=language_code)
            obj.set_current_language(language_code)  # NOTE. Explicitly set language to the state the object was fetched in.
            return obj
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(u"No published {0} found for the path '{1}'".format(self.model.__name__, path))

    def best_match_for_path(self, path, language_code=None):
        """
        Return the UrlNode that is the closest parent to the given path.

        UrlNode.objects.best_match_for_path('/photos/album/2008/09') might return the page with url '/photos/album/'.

        .. versionchanged:: 0.9 This filter only returns the pages of the current site.
        """
        if language_code is None:
            language_code = self._language or get_language()

        # Based on FeinCMS:
        paths = self._split_path_levels(path)

        try:
            qs = self._single_site() \
                     .filter(translations___cached_url__in=paths, translations__language_code=language_code) \
                     .extra(select={'_url_length': 'LENGTH(_cached_url)'}) \
                     .order_by('-level', '-_url_length')  # / and /news/ is both level 0
            obj = qs[0]
            obj.set_current_language(language_code)  # NOTE: Explicitly set language to the state the object was fetched in.
            return obj
        except IndexError:
            raise self.model.DoesNotExist(u"No published {0} found for the path '{1}'".format(self.model.__name__, path))

    def _split_path_levels(self, path):
        """
        Split the URL path, used by best_match_for_path()
        """
        # This is a separate function to allow unit testing.
        paths = []
        if path:
            tokens = path.rstrip('/').split('/')
            paths += [u'{0}/'.format(u'/'.join(tokens[:i])) for i in range(1, len(tokens) + 1)]

            # If the original URL didn't end with a slash,
            # make sure the splitted path also doesn't.
            if path[-1] != '/':
                paths[-1] = paths[-1].rstrip('/')

        return paths

    def get_for_key(self, key):
        """
        Return the UrlNode for the given key.

        The key can be a slug-like value that was configured in ``FLUENT_PAGES_KEY_CHOICES``.
        """
        qs = self._single_site()
        try:
            return qs.get(key=key)
        except self.model.DoesNotExist as e:
            if self._parent_site is not None:
                raise self.model.DoesNotExist("{0} with key='{1}' does not exist in site {2}.".format(self.model.__name__, key, self._parent_site))
            else:
                raise self.model.DoesNotExist("{0} with key='{1}' does not exist.".format(self.model.__name__, key))

    def parent_site(self, site):
        """
        .. versionadded:: 0.9 Filter to the given site.
        """
        # Since .published() calls ._single_site(), this already filters the queryset.
        # Make sure .parent_site() is used first.
        assert self._parent_site is None, "Can't filter for a parent_site() twice. Perhaps .published() was already used?"

        # Avoid auto filter if site is already set.
        self._parent_site = site
        return self.filter(parent_site=site)

    def _single_site(self):
        """
        Make sure the queryset is filtered on a parent site, if that didn't happen already.
        """
        if appsettings.FLUENT_PAGES_FILTER_SITE_ID and self._parent_site is None:
            return self.parent_site(settings.SITE_ID)
        else:
            return self

    def published(self, for_user=None):
        """
        Return only published pages for the current site.

        .. versionchanged:: 0.9 This filter only returns the pages of the current site.
        """
        from fluent_pages.models import UrlNode   # the import can't be globally, that gives a circular dependency

        if for_user is not None and for_user.is_staff:
            return self._single_site()

        return self \
            ._single_site() \
            .filter(status=UrlNode.PUBLISHED) \
            .filter(
                Q(publication_date__isnull=True) |
                Q(publication_date__lt=now())
            ).filter(
                Q(publication_end_date__isnull=True) |
                Q(publication_end_date__gte=now())
            )

    def in_navigation(self, for_user=None):
        """
        Return only pages in the navigation.
        """
        return self.published(for_user=for_user).filter(in_navigation=True)

    def in_sitemaps(self):
        """
        .. versionadded:: 0.9
        Return only pages that should be listed in the sitemap
        """
        return self.published().filter(in_sitemaps=True)

    def url_pattern_types(self):
        """
        Return only page types which have a custom URLpattern attached.
        """
        from fluent_pages.extensions import page_type_pool
        return self.filter(polymorphic_ctype_id__in=(page_type_pool.get_url_pattern_types()))

    def toplevel(self):
        """
        Return all pages which have no parent.
        """
        return self.filter(parent__isnull=True, level=0)

    def _mark_current(self, current_page):
        """
        Internal API to mark the given page as "is_current" in the resulting set.
        """
        if current_page:
            current_id = current_page.id

            def add_prop(obj):
                obj.is_current = (obj.id == current_id)

            return self.decorate(add_prop)
        else:
            return self


class UrlNodeManager(PolymorphicMPTTModelManager, TranslatableManager):
    """
    Extra methods attached to ``UrlNode.objects`` and ``Page.objects``.
    """
    queryset_class = UrlNodeQuerySet

    # NOTE: Fetching the queryset is done by calling self.all() here on purpose.
    # By using .all(), the proper get_query_set()/get_queryset() will be used for each Django version.
    # Django 1.4/1.5 need to use get_query_set(), because the RelatedManager overrides that.

    def get_for_path(self, path, language_code=None):
        """
        Return the UrlNode for the given path.
        The path is expected to start with an initial slash.

        Raises UrlNode.DoesNotExist when the item is not found.

        .. versionchanged:: 0.9 This filter only returns the pages of the current site.
        """
        return self.all().get_for_path(path, language_code=language_code)

    def best_match_for_path(self, path, language_code=None):
        """
        Return the UrlNode that is the closest parent to the given path.

        UrlNode.objects.best_match_for_path('/photos/album/2008/09') might return the page with url '/photos/album/'.

        .. versionchanged:: 0.9 This filter only returns the pages of the current site.
        """
        return self.all().best_match_for_path(path, language_code=language_code)

    def get_for_key(self, key):
        """
        .. versionadded:: 0.9 Return the UrlNode for the given key.

        The key can be a slug-like value that was configured in ``FLUENT_PAGES_KEY_CHOICES``.
        """
        return self.all().get_for_key(key)

    def parent_site(self, site):
        """
        .. versionadded:: 0.9 Filter to the given site.
        """
        return self.all().parent_site(site)

    def published(self, for_user=None):
        """
        Return only published pages for the current site.

        .. versionchanged:: 0.9 This filter only returns the pages of the current site.
        """
        return self.all().published(for_user=for_user)

    def in_navigation(self, for_user=None):
        """
        Return only pages in the navigation.
        """
        return self.all().in_navigation(for_user=for_user)

    def in_sitemaps(self):
        """
        .. versionadded:: 0.9
        Return only pages in the navigation.
        """
        return self.all().in_sitemaps()

    def toplevel(self):
        """
        Return all pages which have no parent.
        """
        return self.all().toplevel()

    def toplevel_navigation(self, current_page=None, for_user=None, language_code=None):
        """
        Return all toplevel items, ordered by menu ordering.

        When current_page is passed, the object values such as 'is_current' will be set.
        """
        qs = self.toplevel().in_navigation(for_user=for_user).non_polymorphic()._mark_current(current_page)

        # Make sure only translated menu items are visible.
        if is_multilingual_project():
            if language_code is None:
                if current_page is None or getattr(current_page, '_fetched_in_fallback_language', False):
                    # Show the menu in the current site language.
                    # When a page is fetched in a fallback, the menu shouldn't change.
                    language_code = get_language()
                else:
                    # This exists to preserve old behavior. Maybe it can be removed:
                    language_code = current_page.get_current_language()

            lang_dict = appsettings.FLUENT_PAGES_LANGUAGES.get_language(language_code)
            if lang_dict['hide_untranslated_menu_items']:
                qs = qs.translated(language_code)
            else:
                qs = qs.active_translations(language_code)

        return qs

    def url_pattern_types(self):
        """
        Return only page types which have a custom URLpattern attached.
        """
        return self.all().url_pattern_types()
