# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
from django.core.exceptions import ObjectDoesNotExist

from fluent_pages import appsettings


def forwards_func(apps, schema_editor):
    UrlNode_Translation = apps.get_model('fluent_pages', 'UrlNode_Translation')
    TextFileTranslation = apps.get_model('textfile', 'TextFileTranslation')
    default_choices = ('en', 'en-us', appsettings.FLUENT_PAGES_DEFAULT_LANGUAGE_CODE)

    for textfile in apps.get_model('textfile', 'TextFile').objects.all():
        available_languages = list(UrlNode_Translation.objects.filter(
            master_id=textfile.id).values_list('language_code', flat=True))

        # Find the first language that is usable.
        # Move the fields to the translation of that language.
        lang = next((code for code in default_choices if code in available_languages), available_languages[0])

        TextFileTranslation.objects.create(
            master_id=textfile.pk,
            language_code=lang,
            content=textfile.content,
        )


def backwards_func(apps, schema_editor):
    TextFileTranslation = apps.get_model('textfile', 'TextFileTranslation')

    # Convert all fields back to the single-language table.
    for textfile in apps.get_model('textfile', 'TextFile').objects.all():
        translations = TextFileTranslation.objects.filter(master_id=textfile.id)
        try:
            # Try default translation
            translation = translations.get(language_code=appsettings.FLUENT_PAGES_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            try:
                # Try internal fallback
                translation = translations.get(language_code__in=('en-us', 'en'))
            except ObjectDoesNotExist:
                # Hope there is a single translation
                translation = translations.get()

        textfile.content = translation.content
        textfile.save()   # As intended: doesn't call UrlNode.save() but Model.save() only.

        
class Migration(migrations.Migration):

    dependencies = [
        ('textfile', '0002_add_translation_model'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
