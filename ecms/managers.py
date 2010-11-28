"""
The manager class for the Enterprise-CMS models
"""
# Import namespaces
from django.db import models
from django.conf import settings

# Import objects
from django.http import Http404
from vdboor.managers import DecoratorManager
from django.contrib.sites.models import Site

# Util functions
from django.forms.models import model_to_dict


class CmsSiteManager(models.Manager):
    """
    Extra methods attached to ```CmsSites.objects```
    """

    def get_current(self, request=None):
        """
        Return the current site.
        """
        # TODO: base current site on request host header.

        from ecms.models import CmsSite   # the import can't be globally, that gives a circular dependency
        id = settings.SITE_ID
        try:
            return CmsSite.objects.get(pk=id)
        except CmsSite.DoesNotExist:
            # Create CmsSite object on demand, populate with existing site values
            # so nothing is overwritten with empty values
            site = Site.objects.get_current()
            wrapper = CmsSite(**model_to_dict(site))
            wrapper.save()
            return wrapper


class CmsObjectManager(DecoratorManager):
    """
    Extra methods attached to ```CmsObjects.objects```
    """

    def get_for_path_or_404(self, path):
        """
        Return the CmsObject for the given path.

        Raises a Http404 error when the object is not found.
        """
        try:
            return self.get_for_path(path)
        except self.model.DoesNotExist:
            raise Http404("No published CmsObject found for the path: '%s'" % path)


    def get_for_path(self, path):
        """
        Return the CmsObject for the given path.

        Raises CmsObject.DoesNotExist when the item is not found.
        """
        stripped = path.strip('/')
        stripped = stripped and u'/%s/' % stripped or '/'
        return self.published().get(_cached_url=stripped)


    def published(self):
        """
        Return only published pages
        """
        from ecms.models import CmsObject   # the import can't be globally, that gives a circular dependency
        return self.get_query_set().filter(status=CmsObject.PUBLISHED)


    def in_navigation(self):
        """
        Return only pages in the navigation.
        """
        return self.published().filter(in_navigation=True)


    def toplevel_navigation(self, current_page=None):
        """
        Return all toplevel items.

        When current_page is passed, the object values such as 'is_current' will be set. 
        """
        items = self.in_navigation().filter(parent__isnull=True)
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
