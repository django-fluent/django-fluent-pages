# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluentpage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FluentPageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('layout', models.ForeignKey(verbose_name='Layout', to='fluent_pages.PageLayout', null=True)),
            ],
            options={
                'abstract': False,
                'permissions': (('change_page_layout', 'Can change Page layout'),),
            },
        ),
        migrations.AlterModelOptions(
            name='fluentpage',
            options={'verbose_name': 'Page', 'verbose_name_plural': 'Pages'},
        ),
        migrations.AddField(
            model_name='fluentpagetranslation',
            name='master',
            field=models.ForeignKey(related_name='page_translations', to='fluentpage.FluentPage'),
        ),
    ]
