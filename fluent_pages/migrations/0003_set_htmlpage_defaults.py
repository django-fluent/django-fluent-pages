# Generated by Django 1.11.4 on 2017-08-05 08:55

from django.db import migrations, models


def _set_defaults(apps, schema_editor):
    HtmlPageTranslation = apps.get_model("fluent_pages", "htmlpagetranslation")
    HtmlPageTranslation.objects.filter(meta_title=None).update(meta_title="")
    HtmlPageTranslation.objects.filter(meta_keywords=None).update(meta_keywords="")
    HtmlPageTranslation.objects.filter(meta_description=None).update(meta_description="")
    HtmlPageTranslation.objects.filter(meta_image=None).update(meta_image="")


def _set_nulls(apps, schema_editor):
    HtmlPageTranslation = apps.get_model("fluent_pages", "htmlpagetranslation")
    HtmlPageTranslation.objects.filter(meta_title="").update(meta_title=None)
    HtmlPageTranslation.objects.filter(meta_keywords="").update(meta_keywords=None)
    HtmlPageTranslation.objects.filter(meta_description="").update(meta_description=None)
    HtmlPageTranslation.objects.filter(meta_image="").update(meta_image=None)


class Migration(migrations.Migration):

    dependencies = [("fluent_pages", "0002_add_htmlpage_meta_image")]

    operations = [migrations.RunPython(_set_defaults, _set_nulls)]
