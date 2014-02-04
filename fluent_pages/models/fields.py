from django.db import models
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
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


class TranslatedForeignKeyDescriptor(ReverseSingleRelatedObjectDescriptor):
    def __get__(self, instance, instance_type=None):
        # let the .parent return an object in the same language as our selves.
        # note: when the object is switched to a different language, this updates the shared/cached parent.
        obj = super(TranslatedForeignKeyDescriptor, self).__get__(instance, instance_type)
        if instance is not None and obj is not None:
            obj.set_current_language(instance.get_current_language())
        return obj


class PageTreeForeignKey(PolymorphicTreeForeignKey):
    """
    A customized version of the :class:`~polymorphic_tree.models.PolymorphicTreeForeignKey`.
    """
    default_error_messages = {
        'no_children_allowed': _("The selected page cannot have sub pages."),
    }

    def contribute_to_class(self, cls, name):
        super(PageTreeForeignKey, self).contribute_to_class(cls, name)
        setattr(cls, self.name, TranslatedForeignKeyDescriptor(self))  # override what ForeignKey does.


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
