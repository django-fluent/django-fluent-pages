"""
The data model to walk through the site contents.
These classes are accesable via the models.

These objects only return the relevant data for the contents
in a fixed, minimalistic, API so template designers can focus on that.
"""
import UserDict
from django.utils.safestring import mark_safe


class CmsObjectRegionDict(UserDict.DictMixin):
    """
    A dictionary for to access the active page items through regions.

    This object is used by ``CmsObject`` to provide the following syntax in the template:
    {{ ecms_page.regions.main }}
    """
    def __init__(self, regions, all_page_items):
        self._regions = regions
        self._cached_keys = None
        self._all_page_items = all_page_items

    def __getitem__(self, key):
        """
        Get all ``CmsPageItem`` objects of a region.
        """
        region_items = [item for item in self._all_page_items if item.region == key]
        if not region_items:
            # If the list is empty, check whether the key exists at all.
            # The special key __main__ could have existed before, it's an internal fallback.
            if key != '__main__' and not self._regions.filter(key=key).count():
                raise KeyError("The region '%s' does not exist in the current layout!" % key)

        # Wrap in a list which can be rendered directly.
        region_items.sort(key=lambda item: item.sort_order)
        return CmsPageItemList(region_items)

    def keys(self):
        """
        Get all region names.
        """
        if not self._cached_keys:
            # this executes the QuerySet.
            # If keys() is never requested, a database query is avoided.
            self._cached_keys = [r.key for r in self._regions]

        return self._cached_keys


    # Just for completeness sake:
    def __setitem__(self, key, value):
        assert all(item.region == key for item in value), "Items must be in the same region as the dictionary key!"
        del self[key]
        self._all_page_items += value

    def __delitem__(self, key):
        self._all_page_items = [item for item in self._all_page_items if item.region != key]


class CmsPageItemList(list):
    def render(self):
        """
        Render all items, this is typically used in templates:
        {{ ecms_page.regions.main }}  <-- points to a CmsPageItemList
        """
        if not self:
            str = u'<!-- no items in this region -->'
        else:
            str = ''.join(item.render() for item in self)
        return mark_safe(str)

    def __unicode__(self):
        # so {{ ecms_page.main_page_items }} also works directly.
        return self.render()