from django.db import models
from django.utils.translation import get_language


class TranslatableModel(models.Model):
    """
    Base model class to handle translations.
    """

    # Consider these fields "protected" or "internal" attributes.
    # Not part of the public API, but used internally in the class hierarchy.
    _translations_field = 'translations'
    _translations_model = None

    class Meta:
        abstract = True


    def __init__(self, *args, **kwargs):
        super(TranslatableModel, self).__init__(*args, **kwargs)
        self._translations_cache = {}
        self._active_language = get_language()


    def _get_translated_model(self, language_code=None):
        """
        Fetch the translated fields model.
        """
        if not language_code:
            language_code = self._active_language

        try:
            return self._translations_cache[language_code]
        except KeyError:
            # Get via self.TRANSLATIONS_FIELD.get(..) so it also uses the prefetch/select_related cache.
            accessor = getattr(self, self._translations_field)
            try:
                object = accessor.get(language_code=language_code)
            except self._translations_model.DoesNotExist:
                object = self._translations_model(
                    language_code=language_code,
                    master=self  # ID might be None at this point
                )

            # Cache and return
            self._translations_cache[language_code] = object
            return object


    def save(self, *args, **kwargs):
        super(TranslatableModel, self).save(*args, **kwargs)
        self.save_translations()


    def save_translations(self):
        # Also save translated strings.
        translations = self._get_translated_model()
        if translations.is_modified:
            if not translations.master_id:  # Might not exist during first construction
                translations.master = self
            translations.save()



class TranslatedFieldsModel(models.Model):
    """
    Base class for the model that holds the translated fields.
    """
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(TranslatedFieldsModel, self).__init__(*args, **kwargs)
        self._original_values = self._get_field_values()

    @property
    def is_modified(self):
        return self._original_values != self._get_field_values()

    def save(self, *args, **kwargs):
        super(TranslatedFieldsModel, self).save(*args, **kwargs)
        self._original_values = self._get_field_values()

    def _get_field_values(self):
        # Return all field values in a consistent (sorted) manner.
        return [getattr(self, field) for field in self._meta.get_all_field_names()]

    @classmethod
    def get_translated_fields(self):
        fields = self._meta.get_all_field_names()
        fields.remove('language_code')
        fields.remove('master')
        return fields

    def __unicode__(self):
        return unicode(self.pk)


class TranslatedAttribute(object):
    """
    Descriptor for translated attributes.
    Currently placed manually on the class (no metaclass magic involved here).
    """
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, instance_type=None):
        if not instance:
            # Return the class attribute when asked for by the admin.
            return instance_type._translations_model._meta.get_field_by_name(self.name)[0]

        return getattr(instance._get_translated_model(), self.name)

    def __set__(self, instance, value):
        translation = instance._get_translated_model()
        setattr(translation, self.name, value)

    def __delete__(self, instance):
        delattr(instance._get_translated_model(), self.name)
