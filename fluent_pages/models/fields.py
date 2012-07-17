from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic_tree.models import PolymorphicTreeForeignKey
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


class PageTreeForeignKey(PolymorphicTreeForeignKey):
    """
    A customized version of the :class:`~polymorphic_tree.models.PolymorphicTreeForeignKey`.
    """
    default_error_messages = {
        'no_children_allowed': _("The selected page cannot have sub pages."),
    }


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    _name_re = "^" + __name__.replace(".", "\.")
    add_introspection_rules([], [
        _name_re + "\.TemplateFilePathField",
        _name_re + "\.PageTreeForeignKey",
    ])
