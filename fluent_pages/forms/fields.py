"""
Extra form fields.
"""
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from mptt.forms import TreeNodeChoiceField
from fluent_pages import appsettings
import os


class TemplateFilePathField(forms.FilePathField):
    """
    The associated formfield to select a template path.
    """
    def __init__(self, *args, **kwargs):
        super(TemplateFilePathField, self).__init__(*args, **kwargs)

        # Make choices relative if requested.
        if appsettings.FLUENT_PAGES_RELATIVE_TEMPLATE_DIR:
            self.choices.sort(key=lambda choice: choice[1])
            self.choices = self.widget.choices = [(filename.replace(self.path, '', 1), title) for filename, title in self.choices]

    def prepare_value(self, value):
        """
        Allow effortlessly switching between relative and absolute paths.
        """
        if appsettings.FLUENT_PAGES_RELATIVE_TEMPLATE_DIR:
            # Turn old absolute paths into relative paths.
            if value and os.path.isabs(value) and value.startswith(self.path):
                value = value[len(self.path):].lstrip('/')
        else:
            # If setting is disabled, turn relative path back to abs.
            if not os.path.isabs(value):
                value = os.path.join(self.path, value)
        return value


class RelativeRootPathField(forms.CharField):
    """
    A ``CharField`` which returns stored URL values relative to the fluent-page root.
    """
    def prepare_value(self, value):
        """
        Convert the database/model value to the displayed value.
        Adds the root of the CMS pages.
        """
        if value and value.startswith('/'):  # value is None for add page.
            root = reverse('fluent-page').rstrip('/')
            value = root + value
        return value

    def to_python(self, value):
        """
        Convert the displayed value to the database/model value.
        Removes the root of the CMS pages.
        """
        root = reverse('fluent-page').rstrip('/')
        value = super(RelativeRootPathField, self).to_python(value)
        if root and value.startswith(root):
            value = value[len(root):]
        return value


class PageChoiceField(TreeNodeChoiceField):
    """
    A SelectBox that displays the pages QuerySet, with items indented.
    """

    def __init__(self, *args, **kwargs):
        if not args and not kwargs.has_key('queryset'):
            from fluent_pages.models import UrlNode
            kwargs['queryset'] = UrlNode.objects.published().non_polymorphic()
            self.custom_qs = False
        else:
            self.custom_qs = True
        super(PageChoiceField, self).__init__(*args, **kwargs)

    def __deepcopy__(self, memo):
        new_self = super(PageChoiceField, self).__deepcopy__(memo)

        if not self.custom_qs:
            # Reevaluate the queryset for django-multisite support.
            # This is needed when SITE_ID is a threadlocal, because .published() freezes the SITE_ID.
            from fluent_pages.models import UrlNode
            mptt_opts = self.queryset.model._mptt_meta
            new_self.queryset = UrlNode.objects.published().non_polymorphic().order_by(mptt_opts.tree_id_attr, mptt_opts.left_attr)

        return new_self

    def label_from_instance(self, page):
        page_title = page.title or page.slug  # TODO: menu title?
        return mark_safe(u"%s %s" % (u"&nbsp;&nbsp;" * page.level, escape(page_title)))
