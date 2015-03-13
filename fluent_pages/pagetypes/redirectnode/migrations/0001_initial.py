# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedirectNode',
            fields=[
                ('urlnode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_pages.UrlNode')),
            ],
            options={
                'db_table': 'pagetype_redirectnode_redirectnode',
                'verbose_name': 'Redirect',
                'verbose_name_plural': 'Redirects',
            },
            bases=('fluent_pages.page',),
        ),
        migrations.CreateModel(
            name='RedirectNodeTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('new_url', models.URLField(max_length=255, verbose_name='New URL')),
                ('redirect_type', models.IntegerField(default=302, help_text="Use 'normal redirect' unless you want to transfer SEO ranking to the new page.", verbose_name='Redirect type', choices=[(302, 'Normal redirect'), (301, 'Permanent redirect (for SEO ranking)')])),
                ('master', models.ForeignKey(related_name='redirect_translations', editable=False, to='redirectnode.RedirectNode', null=True)),
            ],
            options={
                'db_table': 'redirectnode_redirectnode_translation',
                'verbose_name': 'Redirect Translation',
                'default_permissions': (),
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='redirectnodetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
