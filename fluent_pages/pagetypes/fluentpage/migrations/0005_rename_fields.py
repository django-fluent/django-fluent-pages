# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluentpage', '0004_remove_fluentpage_layout'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fluentpagetranslation',
            old_name='layout_translated',
            new_name='layout',
        ),
    ]
