import django
from django.db import models
from django.db.models.fields.related import ForwardManyToOneDescriptor
from django.utils.translation import gettext_lazy as _
from polymorphic_tree.models import PolymorphicTreeForeignKey

from fluent_pages import forms


class TemplateFilePathField(models.FilePathField):
    """
    A field to select a template path.
    """

    def __init__(self, verbose_name=None, path="", **kwargs):
        defaults = dict(match=r".*\.html$", recursive=True)
        defaults.update(kwargs)
        super().__init__(verbose_name, path=path, **defaults)

    def formfield(self, **kwargs):
        # Like the FilePathField, the formfield does the actual work
        defaults = {"form_class": forms.TemplateFilePathField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if "path" in kwargs:
            del kwargs["path"]
        return name, path, args, kwargs


class TranslatedForeignKeyDescriptor(ForwardManyToOneDescriptor):
    def __get__(self, instance, instance_type=None):
        # let the .parent return an object in the same language as our selves.
        # note: when the object is switched to a different language, this updates the shared/cached parent.
        obj = super().__get__(instance, instance_type)
        if instance is not None and obj is not None:
            obj.set_current_language(instance.get_current_language())
        return obj


class PageTreeForeignKey(PolymorphicTreeForeignKey):
    """
    A customized version of the :class:`~polymorphic_tree.models.PolymorphicTreeForeignKey`.
    """

    default_error_messages = {
        "required": _("This page type should have a parent."),
        "no_children_allowed": _("The selected page cannot have sub pages."),
        "child_not_allowed": _("The selected page cannot have this page type as a child!"),
    }

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(
            cls, self.name, TranslatedForeignKeyDescriptor(self)
        )  # override what ForeignKey does.
