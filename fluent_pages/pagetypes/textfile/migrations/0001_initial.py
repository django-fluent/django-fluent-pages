# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextFile',
            fields=[
                ('urlnode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_pages.UrlNode', on_delete=models.CASCADE)),
                ('content', models.TextField(verbose_name='File contents')),
                ('content_type', models.CharField(default='text/plain', max_length=100, verbose_name='File type', choices=[('text/plain', 'Plain text'), ('text/xml', 'XML'), ('text/html', 'HTML')])),
            ],
            options={
                'db_table': 'pagetype_textfile_textfile',
                'verbose_name': 'Plain text file',
                'verbose_name_plural': 'Plain text files',
            },
            bases=('fluent_pages.page',),
        ),
    ]
