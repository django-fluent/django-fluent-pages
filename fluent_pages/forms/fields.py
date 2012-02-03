"""
Extra form fields.
"""
from django import forms
from django.core.urlresolvers import reverse
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
    A ``CharField`` which returns stored URL values relative to the ecms-pages root.
    """
    def prepare_value(self, value):
        """
        Convert the database/model value to the displayed value.
        Adds the root of the CMS pages.
        """
        if value and value.startswith('/'):  # value is None for add page.
            root = reverse('ecms-page').rstrip('/')
            value = root + value
        return value

    def to_python(self, value):
        """
        Convert the displayed value to the database/model value.
        Removes the root of the CMS pages.
        """
        root = reverse('ecms-page').rstrip('/')
        value = super(RelativeRootPathField, self).to_python(value)
        if root and value.startswith(root):
            value = value[len(root):]
        return value
