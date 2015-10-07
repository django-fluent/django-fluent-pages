# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('textfile', '0003_migrate_translatable_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textfile',
            name='content',
        ),
    ]
