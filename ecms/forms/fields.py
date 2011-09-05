"""
Extra form fields.
"""
from django import forms
from ecms import appsettings
import os


class TemplateFilePathField(forms.FilePathField):
    """
    The associated formfield to select a template path.
    """
    def __init__(self, *args, **kwargs):
        super(TemplateFilePathField, self).__init__(*args, **kwargs)

        # Make choices relative if requested.
        if appsettings.ECMS_RELATIVE_TEMPLATE_DIR:
            self.choices = self.widget.choices = [(f.replace(self.path, '', 1), t) for f, t in self.choices]

    def prepare_value(self, value):
        """
        Allow effortlessly switching between relative and absolute paths.
        """
        if appsettings.ECMS_RELATIVE_TEMPLATE_DIR:
            # Turn old absolute paths into relative paths.
            if os.path.isabs(value) and value.startswith(self.path):
                value = value[len(self.path):].lstrip('/')
        else:
            # If setting is disabled, turn relative path back to abs.
            if not os.path.isabs(value):
                value = os.path.join(self.path, value)
        return value
