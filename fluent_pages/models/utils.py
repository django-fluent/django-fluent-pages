"""
Custom generic managers
"""
import django
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.query import QuerySet


def prefill_parent_site(page):
    """
    Optimize the ``parent_site`` field of a page if possible, fill it's cache.
    """
    if Site._meta.installed:
        current_site = Site.objects.get_current()

        if page.parent_site_id == current_site.id:
            page.parent_site = current_site  # Fill the ORM cache.


# Based on django-queryset-transform.
# This object however, operates on a per-object instance
# without breaking the result generators


class DecoratingQuerySet(QuerySet):
    """
    An enhancement of the QuerySet which allows objects to be decorated
    with extra properties before they are returned.

    When using this method with *django-polymorphic* or *django-hvad*, make sure this
    class is first in the chain of inherited classes.
    """

    def __init__(self, *args, **kwargs):
        super(DecoratingQuerySet, self).__init__(*args, **kwargs)
        self._decorate_funcs = []

    def _clone(self, *args, **kwargs):
        c = super(DecoratingQuerySet, self)._clone(*args, **kwargs)
        c._decorate_funcs = self._decorate_funcs
        return c

    def decorate(self, fn):
        """
        Register a function which will decorate a retrieved object before it's returned.
        """
        if fn not in self._decorate_funcs:
            self._decorate_funcs.append(fn)
        return self

    def iterator(self):
        """
        Overwritten iterator which will apply the decorate functions before returning it.
        """
        base_iterator = super(DecoratingQuerySet, self).iterator()
        for obj in base_iterator:
            # Apply the decorators
            for fn in self._decorate_funcs:
                fn(obj)

            yield obj


class DecoratorManager(models.Manager):
    """
    The manager class which ensures the enhanced DecoratorQuerySet object is used.
    """

    def get_queryset(self):
        return DecoratingQuerySet(self.model, using=self._db)

    if django.VERSION < (1, 8):
        get_query_set = get_queryset
