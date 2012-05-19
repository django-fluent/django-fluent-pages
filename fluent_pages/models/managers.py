"""
The manager class for the CMS models
"""
from datetime import datetime
from django.db.models.query_utils import Q
from mptt.managers import TreeManager
from polymorphic import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet
from fluent_pages.utils.db import DecoratingQuerySet


class UrlNodeQuerySet(PolymorphicQuerySet, DecoratingQuerySet):
    def get_for_path(self, path):
        """
        Return the UrlNode for the given path.
        The path is expected to start with an initial slash.

        Raises UrlNode.DoesNotExist when the item is not found.
        """
        # Don't normalize slashes, expect the URLs to be sane.
        try:
            return self.get(_cached_url=path)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist("No published {0} found for the path '{1}'".format(self.model.__name__, path))


    def best_match_for_path(self, path):
        """
        Return the UrlNode that is the closest parent to the given path.

        UrlNode.objects.best_match_for_path('/photos/album/2008/09') might return the page with url '/photos/album/'.
        """
        # from FeinCMS:
        paths = []
        if path:
            tokens = path.rstrip('/').split('/')
            paths += ['{0}/'.format('/'.join(tokens[:i])) for i in range(1, len(tokens) + 1)]

        try:
            return self.filter(_cached_url__in=paths) \
                       .extra(select={'_url_length': 'LENGTH(_cached_url)'}) \
                       .order_by('-_url_length')[0]
        except IndexError:
            raise self.model.DoesNotExist("No published {0} found for the path '{1}'".format(self.model.__name__, path))


    def published(self):
        """
        Return only published pages
        """
        from fluent_pages.models import UrlNode   # the import can't be globally, that gives a circular dependency
        return self \
            .filter(status=UrlNode.PUBLISHED) \
            .filter(
                Q(publication_date__isnull=True) |
                Q(publication_date__lt=datetime.now())
            ).filter(
                Q(publication_end_date__isnull=True) |
                Q(publication_end_date__gte=datetime.now())
            )


    def in_navigation(self):
        """
        Return only pages in the navigation.
        """
        return self.published().filter(in_navigation=True)


    def toplevel(self):
        """
        Return all pages which have no parent.
        """
        return self.filter(parent__isnull=True)



class UrlNodeManager(TreeManager, PolymorphicManager):
    """
    Extra methods attached to ``UrlNode.objects`` and ``Page.objects``.
    """

    def __init__(self, *args, **kwargs):
        PolymorphicManager.__init__(self, UrlNodeQuerySet, *args, **kwargs)


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
        items = self.toplevel().in_navigation().non_polymorphic()
        if current_page:
            items = _mark_current(items, current_page)
        return items


# Implemented as method, to avoid overwriting the QuerySet once again.
def _mark_current(qs, current_page):
    """
    Mark the given page as "is_current" in the resulting set.
    """
    current_id = current_page.id

    def add_prop(obj):
        obj.is_current = (obj.id == current_id)

    return qs.decorate(add_prop)
