# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fluent_pages.models.db
from fluent_pages import appsettings
from django.conf import settings
import fluent_pages.models.fields
import slug_preview.models


def make_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    Site.objects.get_or_create(
        pk=settings.SITE_ID,
        defaults=dict(
            name='example',
            domain='example.com',
        ))


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
            name='HtmlPageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('meta_keywords', models.CharField(max_length=255, null=True, verbose_name='keywords', blank=True)),
                ('meta_description', models.CharField(max_length=255, null=True, verbose_name='description', blank=True)),
                ('meta_title', models.CharField(help_text='When this field is not filled in, the menu title text will be used.', max_length=255, null=True, verbose_name='page title', blank=True)),
            ],
            options={
                'db_table': 'fluent_pages_htmlpage_translation',
                'verbose_name': 'SEO Translation',
                'verbose_name_plural': 'SEO Translations',
                'default_permissions': (),
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageLayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(help_text='A short name to identify the layout programmatically', verbose_name='key')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('template_path', fluent_pages.models.fields.TemplateFilePathField(verbose_name='template file', recursive=True, match='.*\\.html$')),
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
                ('status', models.CharField(default='d', max_length=1, verbose_name='status', db_index=True, choices=[('p', 'Published'), ('d', 'Draft')])),
                ('publication_date', models.DateTimeField(help_text='When the page should go live, status must be "Published".', null=True, verbose_name='publication date', db_index=True, blank=True)),
                ('publication_end_date', models.DateTimeField(db_index=True, null=True, verbose_name='publication end date', blank=True)),
                ('in_navigation', models.BooleanField(default=True, db_index=True, verbose_name='show in navigation')),
                ('in_sitemaps', models.BooleanField(default=True, db_index=True, verbose_name='include in search engine sitemaps')),
                ('key', models.SlugField(blank=True, help_text='A unique identifier that is used for linking to this page.', null=True, verbose_name='page identifier', choices=appsettings.FLUENT_PAGES_KEY_CHOICES)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='last modification')),
                ('author', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('parent', fluent_pages.models.fields.PageTreeForeignKey(related_name='children', blank=True, to='fluent_pages.UrlNode', help_text='You can also change the parent by dragging the page in the list.', null=True, verbose_name='parent')),
                ('parent_site', models.ForeignKey(default=fluent_pages.models.db._get_current_site, editable=False, to='sites.Site')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_fluent_pages.urlnode_set+', editable=False, to='contenttypes.ContentType', null=True)),
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
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('slug', slug_preview.models.SlugPreviewField(help_text='The slug is used in the URL of the page', max_length=100, verbose_name='slug')),
                ('override_url', models.CharField(help_text="Override the target URL. Be sure to include slashes at the beginning and at the end if it is a local URL. This affects both the navigation and subpages' URLs.", max_length=255, verbose_name='Override URL', blank=True)),
                ('_cached_url', models.CharField(db_index=True, max_length=255, null=True, editable=False, blank=True)),
                ('master', models.ForeignKey(related_name='translations', to='fluent_pages.UrlNode', null=True)),
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
        migrations.CreateModel(
            name='HtmlPage',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name_plural': 'Pages',
            },
            bases=('fluent_pages.page',),
        ),
        migrations.AddField(
            model_name='htmlpagetranslation',
            name='master',
            field=models.ForeignKey(related_name='seo_translations', editable=False, to='fluent_pages.HtmlPage', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='htmlpagetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
