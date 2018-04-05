"""
Extra form fields.
"""
import os

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from fluent_pages import appsettings
from mptt.forms import TreeNodeChoiceField



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
        if value is not None:
            if appsettings.FLUENT_PAGES_RELATIVE_TEMPLATE_DIR:
                # Turn old absolute paths into relative paths.
                if os.path.isabs(value) and value.startswith(self.path):
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

    def __init__(self, *args, **kwargs):
        super(RelativeRootPathField, self).__init__(*args, **kwargs)
        self.language_code = get_language()

    def bound_data(self, data, initial):
        """
        Make sure the BoundField.value() doesn't pass the displayed value to prepare_value() again.
        Strip the root from the value, allowing prepare_value() to add it again.
        """
        return self.to_python(data)

    def prepare_value(self, value):
        """
        Convert the database/model value to the displayed value.
        Adds the root of the CMS pages.
        """
        if value and value.startswith('/'):  # value is None for add page.
            root = self.get_root(value)
            value = root + value
        return value

    def to_python(self, value):
        """
        Convert the displayed value to the database/model value.
        Removes the root of the CMS pages.
        """
        root = self.get_root(value)
        value = super(RelativeRootPathField, self).to_python(value)
        if root and value.startswith(root):
            value = value[len(root):]
        return value

    def get_root(self, value):
        with translation.override(self.language_code):
            return reverse('fluent-page').rstrip('/')


class PageChoiceField(TreeNodeChoiceField):
    """
    A SelectBox that displays the pages QuerySet, with items indented.
    """
    default_error_messages = {
        'not_published': _("The selected page is not published."),
    }

    def __init__(self, *args, **kwargs):
        if not args and 'queryset' not in kwargs:
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

    def clean(self, value):
        """
        Try to come up with a better error message for unpublished pages.
        """
        try:
            # either to_python() or validate() can check the model
            return super(PageChoiceField, self).clean(value)
        except ValidationError as e:
            if e.code == 'invalid_choice':
                if self._is_unpublished(value):
                    raise ValidationError(
                        self.error_messages['not_published'],
                        code='invalid_choice,'
                    )

            raise

    def _is_unpublished(self, value):
        from fluent_pages.models import UrlNode
        try:
            page = UrlNode.objects.non_polymorphic().get_for_id(int(value))
        except (ValueError, UrlNode.DoesNotExist):
            return None
        else:
            return not page.is_published

    def label_from_instance(self, page):
        page_title = page.title or page.slug  # TODO: menu title?
        return mark_safe(u"%s %s" % (u"&nbsp;&nbsp;" * page.level, escape(page_title)))
