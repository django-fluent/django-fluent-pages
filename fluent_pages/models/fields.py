import django
from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic_tree.models import PolymorphicTreeForeignKey
from fluent_utils.django_compat import ForwardManyToOneDescriptor
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

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = "{0}.{1}".format(self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        del kwargs['path']
        return (field_class, args, kwargs)

    def deconstruct(self):
        # For Django 1.7 migrations
        name, path, args, kwargs = super(TemplateFilePathField, self).deconstruct()
        if 'path' in kwargs:
            del kwargs["path"]
        return name, path, args, kwargs


class TranslatedForeignKeyDescriptor(ForwardManyToOneDescriptor):

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

    def contribute_to_class(self, cls, name, virtual_only=False):
        if django.VERSION >= (1, 8):
            super(PageTreeForeignKey, self).contribute_to_class(cls, name, virtual_only=virtual_only)
        else:
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
