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
                ('layout', models.ForeignKey(verbose_name='Layout', to='fluent_pages.PageLayout', null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'pagetype_fluentpage_fluentpage',
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
                'permissions': (('change_page_layout', 'Can change Page layout'),),
            },
            bases=('fluent_pages.htmlpage',),
        ),
    ]
