# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FluentPage',
            fields=[
                ('urlnode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_pages.UrlNode')),
                ('meta_keywords', models.CharField(max_length=255, null=True, verbose_name='keywords', blank=True)),
                ('meta_description', models.CharField(max_length=255, null=True, verbose_name='description', blank=True)),
                ('meta_title', models.CharField(help_text='When this field is not filled in, the menu title text will be used.', max_length=255, null=True, verbose_name='page title', blank=True)),
                ('layout', models.ForeignKey(verbose_name='Layout', to='fluent_pages.PageLayout', null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
                'permissions': (('change_page_layout', 'Can change Page layout'),),
            },
            bases=('fluent_pages.page', models.Model),
        ),
    ]
