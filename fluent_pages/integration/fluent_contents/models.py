"""
The model integration.
Everything can be imported from ``__init__.py``.
"""
from __future__ import absolute_import
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import Placeholder
from fluent_contents.models.fields import PlaceholderRelation, ContentItemRelation
from fluent_pages.models import HtmlPage


class FluentContentsPage(HtmlPage):
    """
    The base model to create a Page object which hosts placeholders and content items.
    """
    # Access to fluent-contents via the model
    # This also makes sure that the admin delete page will list the models
    # because they are liked via a GenericForeignKey

    #: Related manager to access all placeholders
    placeholder_set = PlaceholderRelation()

    #: Related manager to access all content items
    contentitem_set = ContentItemRelation()

    class Meta:
        abstract = True
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    def create_placeholder(self, slot, role='m', title=None):
        """
        Create a placeholder on this page.

        To fill the content items, use
        :func:`ContentItemModel.objects.create_for_placeholder() <fluent_contents.models.managers.ContentItemManager.create_for_placeholder>`.

        :rtype: :class:`~fluent_contents.models.Placeholder`
        """
        return Placeholder.objects.create_for_object(self, slot, role=role, title=title)

    def get_placeholder_by_slot(self, slot):
        """
        Return a placeholder that is part of this page.
        :rtype: :class:`~fluent_contents.models.Placeholder`
        """
        return self.placeholder_set.filter(slot=slot)

    def get_content_items_by_slot(self, slot):
        """
        Return all content items of the page, which are stored in the given slot name.
        :rtype: :class:`~fluent_contents.models.manager.ContentItemQuerySet`
        """
        # Placeholder.objects.get_by_slot(self, slot)
        placeholder = self.placeholder_set.filter(slot=slot)
        return self.contentitem_set.filter(placeholder=placeholder)
