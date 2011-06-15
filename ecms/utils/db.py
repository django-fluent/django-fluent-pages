"""
Custom generic managers
"""
from django.db import models
from django.db.models.query import QuerySet


# Based on django-queryset-transform.
# This object however, operates on a per-object instance
# without breaking the result generators


class DecoratingQuerySet(QuerySet):
    """
    An enhancement of the QuerySet which allows objects to be decorated
    with extra properties before they are returned.
    """

    def __init__(self, *args, **kwargs):
        super(DecoratingQuerySet, self).__init__(*args, **kwargs)
        self._decorate_funcs = []

    def _clone(self, klass=None, setup=False, **kw):
        c = super(DecoratingQuerySet, self)._clone(klass, setup, **kw)
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
    def get_query_set(self):
        return DecoratingQuerySet(self.model)
