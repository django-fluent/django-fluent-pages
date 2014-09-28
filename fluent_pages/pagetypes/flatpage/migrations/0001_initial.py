# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlatPage',
            fields=[
                ('urlnode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_pages.UrlNode')),
                ('meta_keywords', models.CharField(max_length=255, null=True, verbose_name='keywords', blank=True)),
                ('meta_description', models.CharField(max_length=255, null=True, verbose_name='description', blank=True)),
                ('meta_title', models.CharField(help_text='When this field is not filled in, the menu title text will be used.', max_length=255, null=True, verbose_name='page title', blank=True)),
                ('template_name', models.CharField(default=b'fluent_pages/pagetypes/flatpage/default.html', max_length=200, null=True, editable=False, verbose_name='Layout')),
                ('content', models.TextField(verbose_name='Content', blank=True)),
            ],
            options={
                'verbose_name': 'Flat Page',
                'verbose_name_plural': 'Flat Pages',
            },
            bases=('fluent_pages.page', models.Model),
        ),
    ]
