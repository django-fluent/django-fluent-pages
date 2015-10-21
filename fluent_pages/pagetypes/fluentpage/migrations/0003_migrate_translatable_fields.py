# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from fluent_pages import appsettings


def forwards_func(apps, schema_editor):
    UrlNode_Translation = apps.get_model('fluent_pages', 'UrlNode_Translation')
    FluentPageTranslation = apps.get_model('fluentpage', 'FluentPageTranslation')

    for fluentpage in apps.get_model('fluentpage', 'FluentPage').objects.all():
        available_languages = list(UrlNode_Translation.objects.filter(
            master_id=fluentpage.pk).values_list('language_code', flat=True))

        for lang in available_languages:
            FluentPageTranslation.objects.create(
                master_id=fluentpage.pk,
                language_code=lang,
                layout=fluentpage.layout,
            )


def backwards_func(apps, schema_editor):
    FluentPageTranslation = apps.get_model('fluentpage', 'FluentPageTranslation')
    FluentPage = apps.get_model('fluentpage', 'FluentPage')
    PageLayout = apps.get_model('fluent_pages', 'PageLayout')

    # Convert all fields back to the single-language table.
    for fluentpage in FluentPage.objects.all():
        translations = FluentPageTranslation.objects.filter(master_id=fluentpage.pk)
        try:
            # Try default translation
            translation = translations.get(language_code=appsettings.FLUENT_PAGES_DEFAULT_LANGUAGE_CODE)
            layout = translation.layout
        except ObjectDoesNotExist:
            try:
                # Try internal fallback
                translation = translations.get(language_code__in=('en-us', 'en'))
                layout = translation.layout
            except ObjectDoesNotExist:
                # Hope there is a single translation
                layout_choices = translations.order_by().distinct().values_list('layout', flat=True)
                if len(layout_choices) > 1:
                    raise MultipleObjectsReturned("There are multiple layout choices for {0}, and no canonical one.".format(fluentpage))
                layout = PageLayout.objects.get(pk=layout_choices[0])

        fluentpage.layout = layout
        fluentpage.save()   # As intended: doesn't call UrlNode.save() but Model.save() only.


class Migration(migrations.Migration):

    dependencies = [
        ('fluentpage', '0002_add_translation_model'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
