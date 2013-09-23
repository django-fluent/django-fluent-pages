"""
The manager class for the CMS models
"""
from django.db.models.query_utils import Q
from django.utils.translation import get_language
from parler import is_multilingual_project
from parler.managers import TranslatableQuerySet
from polymorphic_tree.managers import PolymorphicMPTTModelManager, PolymorphicMPTTQuerySet
from fluent_pages import appsettings
from fluent_pages.utils.db import DecoratingQuerySet
from fluent_pages.utils.compat import now


class UrlNodeQuerySet(TranslatableQuerySet, DecoratingQuerySet, PolymorphicMPTTQuerySet):
    def get_for_path(self, path, language_code=None):
        """
        Return the UrlNode for the given path.
        The path is expected to start with an initial slash.

        Raises UrlNode.DoesNotExist when the item is not found.
        """
        if language_code is None:
            language_code = get_language()

        # Don't normalize slashes, expect the URLs to be sane.
        try:
            object = self.get(translations___cached_url=path, translations__language_code=language_code)
            object.set_current_language(language_code)  # NOTE. Explicitly set language to the state the object was fetched in.
            return object
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(u"No published {0} found for the path '{1}'".format(self.model.__name__, path))


    def best_match_for_path(self, path, language_code=None):
        """
        Return the UrlNode that is the closest parent to the given path.

        UrlNode.objects.best_match_for_path('/photos/album/2008/09') might return the page with url '/photos/album/'.
        """
        if language_code is None:
            language_code = get_language()

        # Based on FeinCMS:
        paths = self._split_path_levels(path)

        try:
            qs = self.filter(translations___cached_url__in=paths, translations__language_code=language_code) \
                     .extra(select={'_url_length': 'LENGTH(_cached_url)'}) \
                     .order_by('-level', '-_url_length')  # / and /news/ is both level 0
            object = qs[0]
            object.set_current_language(language_code)  # NOTE: Explicitly set language to the state the object was fetched in.
            return object
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


    def published(self):
        """
        Return only published pages
        """
        from fluent_pages.models import UrlNode   # the import can't be globally, that gives a circular dependency
        return self \
            .filter(status=UrlNode.PUBLISHED) \
            .filter(
                Q(publication_date__isnull=True) |
                Q(publication_date__lt=now())
            ).filter(
                Q(publication_end_date__isnull=True) |
                Q(publication_end_date__gte=now())
            )


    def in_navigation(self):
        """
        Return only pages in the navigation.
        """
        return self.published().filter(in_navigation=True)


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
        return self.filter(parent__isnull=True)


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



class UrlNodeManager(PolymorphicMPTTModelManager):
    """
    Extra methods attached to ``UrlNode.objects`` and ``Page.objects``.
    """
    queryset_class = UrlNodeQuerySet


    def get_for_path(self, path):
        """
        Return the UrlNode for the given path.

        Raises UrlNode.DoesNotExist when the item is not found.
        """
        return self.get_query_set().get_for_path(path)


    def best_match_for_path(self, path):
        """
        Return the UrlNode that is the closest parent to the given path.

        UrlNode.objects.best_match_for_path('/photos/album/2008/09') might return the page with url '/photos/album/'.
        """
        return self.get_query_set().best_match_for_path(path)


    def published(self):
        """
        Return only published pages
        """
        return self.get_query_set().published()


    def in_navigation(self):
        """
        Return only pages in the navigation.
        """
        return self.get_query_set().in_navigation()


    def toplevel(self):
        """
        Return all pages which have no parent.
        """
        return self.get_query_set().toplevel()


    def toplevel_navigation(self, current_page=None):
        """
        Return all toplevel items, ordered by menu ordering.

        When current_page is passed, the object values such as 'is_current' will be set. 
        """
        qs = self.toplevel().in_navigation().non_polymorphic()._mark_current(current_page)

        if is_multilingual_project():
            # Make sure only translated menu items are visible.
            language = get_language()
            fallback = appsettings.get_language_settings(language).get('fallback')

            if fallback and fallback != language:
                qs = qs.filter(translations__language_code__in=(language, fallback)).distinct()
            else:
                qs = qs.filter(translations__language_code=language)

        return qs
