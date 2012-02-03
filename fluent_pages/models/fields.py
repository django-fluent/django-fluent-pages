from django.db import models
from fluent_pages import forms


class TemplateFilePathField(models.FilePathField):
    """
    A field to select a template path.
    """
    def __init__(self, verbose_name=None, path='', **kwargs):
        defaults = dict(match=r'.*\.html$', recursive=True)
        defaults.update(kwargs)
        super(TemplateFilePathField, self).__init__(verbose_name, path=path, **defaults)

    def formfield(self, **kwargs):
        # Like the FilePathField, the formfield does the actual work
        defaults = {'form_class': forms.TemplateFilePathField}
        defaults.update(kwargs)
        return super(TemplateFilePathField, self).formfield(**defaults)


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^" + __name__.replace(".", "\.") + "\.TemplateFilePathField"])
