"""
The data model to walk through the site navigation.

These objects only return the relevant data for the menu/breadcrumb
in a fixed, minimalistic, API so template designers can focus on that.

To walk through the site content in Python code, use the :class:`~fluent_pages.models.Page` model directly.
It offers properties such as :attr:`~fluent_pages.models.Page.parent`
and :attr:`~fluent_pages.models.Page.children` (a :class:`~django.db.models.RelatedManager`),
and methods such as `get_parent()` and `get_children()` through the `MPTTModel` base class.
"""
from future.builtins import object
from django.utils.encoding import python_2_unicode_compatible
from parler.models import TranslationDoesNotExist


@python_2_unicode_compatible
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
        return ['slug', 'title', 'url', 'is_active', 'level', 'parent', 'children', 'has_children', 'page']

    # All properties the template can request:
    slug = property(_not_implemented, doc='The slug of the node.')
    title = property(_not_implemented, doc='The title of the node.')
    url = property(_not_implemented, doc='The URL of the node.')
    is_active = property(_not_implemented, doc='True if the node is the currently active page.')
    is_child_active = property(_not_implemented, doc='True if a child of this node is the currently active page.')
    is_published = property(_not_implemented, doc='True if the node is a normal published item.')
    is_draft = property(_not_implemented, doc='True if the node is a draft item.')
    level = property(_not_implemented, doc='The depth of the menu level.')
    parent = property(_not_implemented, doc='The parent node.')
    children = property(_not_implemented, doc='The list of children.')
    has_children = property(_not_implemented, doc='Whether the node has children.')
    page = None

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
        try:
            url = self.url
        except TranslationDoesNotExist:
            url = None
        return '<{0}: {1}>'.format(self.__class__.__name__, url)

    def __str__(self):
        # This only exists in case a developer uses `{{ node }}` in the template.
        try:
            return self.title
        except TranslationDoesNotExist:
            return ''


class PageNavigationNode(NavigationNode):
    """
    An implementation of the :class:`NavigationNode` for :class:`~fluent_pages.models.Page` models.
    """

    def __init__(self, page, parent_node=None, max_depth=9999, current_page=None, for_user=None):
        """
        Initialize the node with a Page.
        """
        assert page.in_navigation, "PageNavigationNode can't take page #%d (%s) which is not visible in the navigation." % (page.id, page.url)
        super(NavigationNode, self).__init__()
        self._page = page
        self._current_page = current_page
        self._parent_node = parent_node
        self._children = None
        self._max_depth = max_depth
        self._user = for_user

        # Depths starts relative to the first level.
        if not parent_node:
            self._max_depth += page.get_level()

    slug = property(lambda self: self._page.slug)
    title = property(lambda self: self._page.title)
    url = property(lambda self: self._page.url)
    level = property(lambda self: self._page.level)

    @property
    def is_active(self):
        return self._page.pk \
               and self._current_page is not None \
               and self._page.pk == self._current_page.pk

    @property
    def is_child_active(self):
        return self._page.pk \
               and self._current_page is not None \
               and self._page.tree_id == self._current_page.tree_id \
               and self._page.level < self._current_page.level

    @property
    def is_published(self):
        return self._page.is_published

    @property
    def is_draft(self):
        return self._page.is_draft

    @property
    def parent(self):
        if not self._parent_node and not self._page.is_root_node():
            self._parent_node = PageNavigationNode(self._page.get_parent(), max_depth=self._max_depth, current_page=self._current_page)
        return self._parent_node

    @parent.setter
    def parent(self, new_parent):
        # Happens when django-mptt finds an object with a different level in the recursetree() / cache_tree_children() code.
        raise AttributeError("can't set attribute 'parent' of '{0}' object.".format(self.__class__.__name__))

    @property
    def children(self):
        self._read_children()
        if self._children is not None:
            for child in self._children:
                if child.pk == self._page.pk:
                    # This happened with the get_query_set() / get_queryset() transition for Django 1.7, affecting Django 1.4/1.5
                    raise RuntimeError("Page #{0} children contained self!".format(self._page.pk))

                yield PageNavigationNode(child, parent_node=self, max_depth=self._max_depth, current_page=self._current_page)

    @property
    def has_children(self):
        # This avoids queries, just checks that rght = lft + 1
        return not self._page.is_leaf_node()

    def _read_children(self):
        if self._children is None and not self._page.is_leaf_node():
            if (self._page.get_level() + 1) < self._max_depth:  # level 0 = toplevel.
                #children = self._page.get_children()  # Via MPTT
                self._children = self._page.children.in_navigation(for_user=self._user)._mark_current(self._current_page)  # Via RelatedManager

                # If the parent wasn't polymorphic, neither will it's children be.
                if self._page.get_real_instance_class() is not self._page.__class__:
                    self._children = self._children.non_polymorphic()

                self._children = list(self._children)

    @property
    def _mptt_meta(self):
        # Needed since django-mptt 0.6.
        # Need to reconsider this design, for now this patch will suffice.
        return self._page._mptt_meta

    @property
    def page(self):
        """
        .. versionadded:: 0.9 Provide access to the underlying page object, if it exists.
        """
        return self._page
