"""
The data model to walk through the site navigation.

These objects only return the relevant data for the menu/breadcrumb
in a fixed, minimalistic, API so template designers can focus on that.

To walk through the site content in programmatic fashion, use the CmsObject directly.
It offers properties such as `parent` and `children` (a RelatedManager),
and methods such as `get_parent()` and `get_children()` through the `MPTTModel` base class.
"""


class NavigationNode(object):
    """
    The base class for all navigation nodes, page-based on virtually inserted ones.
    """

    # Off course, the subclasses could just implement
    # the same properties (signature-based polymorphism)
    # but I like some explicitness and clarity for a public exposed object.

    def _not_implemented(self):
        raise NotImplementedError("Missing property in NavigationNode!")

    def __dir__(self):
        return ['slug', 'title', 'url', 'is_active', 'parent', 'children']

    # All properties the template can request:
    slug = property(_not_implemented)
    title = property(_not_implemented)
    url = property(_not_implemented)
    is_active = property(_not_implemented)
    level = property(_not_implemented)
    parent = property(_not_implemented)
    children = property(_not_implemented)
    has_children = property(_not_implemented)

    # TODO: active trail item

    # --- Compatibility with mptt recursetree
    # If it looks like a duck and quacks like a duck, it must be a duck.
    # http://docs.python.org/glossary.html#term-duck-typing

    def get_children(self):
        """Provided for compatibility with mptt recursetree"""
        return self.children

    def get_level(self):
        """Provided for compatibility with mptt recursetree"""
        return self.level


class CmsObjectNavigationNode(NavigationNode):

    def __init__(self, page, parent_node=None, max_depth=9999):
        """
        Initialize the node with a CmsObject.
        """
        assert page.in_navigation, "CmsObjectNavigationNode can't take page #%d (%s) which is not visible in the navigation." % (page.id, page.url)
        super(NavigationNode, self).__init__()
        self._page = page
        self._parent_node = parent_node
        self._children = []
        self._max_depth = max_depth

        # Depths starts relative to the first level.
        if not parent_node:
            self._max_depth += page.get_level()


    slug = property(lambda self: self._page.slug)
    title = property(lambda self: self._page.title)
    url = property(lambda self: self._page.url)
    is_active = property(lambda self: self._page.is_current)
    level = property(lambda self: self._page.level)

    @property
    def parent(self):
        if not self._parent_node:
            self._parent_node = CmsObjectNavigationNode(self._page.get_parent(), max_depth=self._max_depth)
        return self._parent_node

    @property
    def children(self):
        self._read_children()
        for child in self._children:
            yield CmsObjectNavigationNode(child, self, max_depth=self._max_depth)

    @property
    def has_children(self):
        self._read_children()
        return self._children.count() > 0

    def _read_children(self):
        if not self._children and (self._page.get_level() + 1) < self._max_depth:  # level 0 = toplevel.
            #children = self._page.get_children()  # Via MPTT
            self._children = self._page.children.in_navigation()  # Via RelatedManager
