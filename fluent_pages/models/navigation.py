"""
The data model to walk through the site navigation.

These objects only return the relevant data for the menu/breadcrumb
in a fixed, minimalistic, API so template designers can focus on that.

To walk through the site content in Python code, use the :class:`~fluent_pages.models.Page` model directly.
It offers properties such as :attr:`~fluent_pages.models.Page.parent`
and :attr:`~fluent_pages.models.Page.children` (a :class:`~django.db.models.RelatedManager`),
and methods such as `get_parent()` and `get_children()` through the `MPTTModel` base class.
"""


class NavigationNode(object):
    """
    The base class for all navigation nodes, whether model-based on virtually inserted ones.
    """

    # Off course, the subclasses could just implement
    # the same properties (signature-based polymorphism)
    # but I like some explicitness and clarity for a public exposed object.

    def _not_implemented(self):
        raise NotImplementedError("Missing property in NavigationNode!")

    def __dir__(self):
        return ['slug', 'title', 'url', 'is_active', 'level', 'parent', 'children', 'has_children']

    # All properties the template can request:
    slug = property(_not_implemented, doc='The slug of the node.')
    title = property(_not_implemented, doc='The title of the node.')
    url = property(_not_implemented, doc='The URL of the node.')
    is_active = property(_not_implemented, doc='True if the node is the currently active page.')
    level = property(_not_implemented, doc='The depth of the menu level.')
    parent = property(_not_implemented, doc='The parent node.')
    children = property(_not_implemented, doc='The list of children.')
    has_children = property(_not_implemented, doc='Whether the node has children.')

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

    # Needed since django-mptt 0.6:
    _mptt_meta = property(_not_implemented)

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self.url)


class PageNavigationNode(NavigationNode):
    """
    An implementation of the :class:`NavigationNode` for :class:`~fluent_pages.models.Page` models.
    """

    def __init__(self, page, parent_node=None, max_depth=9999, current_page=None):
        """
        Initialize the node with a Page.
        """
        assert page.in_navigation, "PageNavigationNode can't take page #%d (%s) which is not visible in the navigation." % (page.id, page.url)
        super(NavigationNode, self).__init__()
        self._page = page
        self._current_page = current_page
        self._parent_node = parent_node
        self._children = []
        self._max_depth = max_depth

        # Depths starts relative to the first level.
        if not parent_node:
            self._max_depth += page.get_level()


    slug = property(lambda self: self._page.slug)
    title = property(lambda self: self._page.title)
    url = property(lambda self: self._page.url)
    level = property(lambda self: self._page.level)

    @property
    def is_active(self):
        return self._page.pk and self._page.pk == self._current_page.pk

    @property
    def parent(self):
        if not self._parent_node and not self._page.is_root_node():
            self._parent_node = PageNavigationNode(self._page.get_parent(), max_depth=self._max_depth, current_page=self._current_page)
        return self._parent_node

    @property
    def children(self):
        self._read_children()
        for child in self._children:
            yield PageNavigationNode(child, parent_node=self, max_depth=self._max_depth, current_page=self._current_page)

    @property
    def has_children(self):
        self._read_children()
        return self._children.count() > 0

    def _read_children(self):
        if not self._children and (self._page.get_level() + 1) < self._max_depth:  # level 0 = toplevel.
            #children = self._page.get_children()  # Via MPTT
            self._children = self._page.children.in_navigation()._mark_current(self._current_page)  # Via RelatedManager

    @property
    def _mptt_meta(self):
        # Needed since django-mptt 0.6.
        # Need to reconsider this design, for now this patch will suffice.
        return self._page._mptt_meta
