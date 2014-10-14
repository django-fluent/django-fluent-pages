# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fluent_pages.pagetypes.redirectnode.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedirectNode',
            fields=[
                ('urlnode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_pages.UrlNode')),
                ('new_url', fluent_pages.pagetypes.redirectnode.fields.UrlField(verbose_name='New URL')),
                ('redirect_type', models.IntegerField(default=302, help_text="Use 'normal redirect' unless you want to transfer SEO ranking to the new page.", verbose_name='Redirect type', choices=[(302, 'Normal redirect'), (301, 'Permanent redirect (for SEO ranking)')])),
            ],
            options={
                'verbose_name': 'Redirect',
                'verbose_name_plural': 'Redirects',
            },
            bases=('fluent_pages.page',),
        ),
    ]
