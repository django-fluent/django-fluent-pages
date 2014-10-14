# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fluent_pages.models.db
from django.conf import settings
import fluent_pages.models.fields


def make_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    if Site.objects.count() == 0:
        site = Site()
        site.pk = settings.SITE_ID
        site.name = 'example'
        site.domain = 'example.com'
        site.save()


def remove_site(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(make_site, reverse_code=remove_site),
        migrations.CreateModel(
            name='PageLayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(help_text='A short name to identify the layout programmatically', verbose_name='key')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('template_path', fluent_pages.models.fields.TemplateFilePathField(verbose_name=b'template file', recursive=True, match=b'.*\\.html$')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Layout',
                'verbose_name_plural': 'Layouts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UrlNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('status', models.CharField(default=b'd', max_length=1, verbose_name='status', db_index=True, choices=[(b'p', 'Published'), (b'd', 'Draft')])),
                ('publication_date', models.DateTimeField(help_text='When the page should go live, status must be "Published".', null=True, verbose_name='publication date', db_index=True, blank=True)),
                ('publication_end_date', models.DateTimeField(db_index=True, null=True, verbose_name='publication end date', blank=True)),
                ('in_navigation', models.BooleanField(default=True, db_index=True, verbose_name='show in navigation')),
                ('in_sitemaps', models.BooleanField(default=True, db_index=True, verbose_name='include in search engine sitemaps')),
                ('key', models.SlugField(blank=True, help_text='A unique identifier that is used for linking to this page.', null=True, verbose_name='page identifier')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='last modification')),
                ('author', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('parent', fluent_pages.models.fields.PageTreeForeignKey(related_name=b'children', blank=True, to='fluent_pages.UrlNode', help_text='You can also change the parent by dragging the page in the list.', null=True, verbose_name='parent')),
                ('parent_site', models.ForeignKey(default=fluent_pages.models.db._get_current_site, editable=False, to='sites.Site')),
                ('polymorphic_ctype', models.ForeignKey(related_name=b'polymorphic_fluent_pages.urlnode_set', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'verbose_name': 'URL Node',
                'verbose_name_plural': 'URL Nodes',
                'permissions': (('change_shared_fields_urlnode', 'Can change Shared fields'), ('change_override_url_urlnode', 'Can change Override URL field')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UrlNode_Translation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('slug', models.SlugField(help_text='The slug is used in the URL of the page', verbose_name='slug')),
                ('override_url', models.CharField(help_text="Override the target URL. Be sure to include slashes at the beginning and at the end if it is a local URL. This affects both the navigation and subpages' URLs.", max_length=300, verbose_name='Override URL', blank=True)),
                ('_cached_url', models.CharField(db_index=True, max_length=300, null=True, editable=False, blank=True)),
                ('master', models.ForeignKey(related_name=b'translations', to='fluent_pages.UrlNode', null=True)),
            ],
            options={
                'verbose_name': 'URL Node translation',
                'verbose_name_plural': 'URL Nodes translations',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='urlnode_translation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='urlnode',
            unique_together=set([('parent_site', 'key')]),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
            ],
            options={
                'verbose_name': 'Page',
                'proxy': True,
                'verbose_name_plural': 'Pages',
            },
            bases=('fluent_pages.urlnode',),
        ),
    ]
