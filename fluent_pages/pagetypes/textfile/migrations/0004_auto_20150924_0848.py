# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('textfile', '0003_auto_20150924_0744'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textfile',
            name='content',
        ),
        migrations.RemoveField(
            model_name='textfile',
            name='content_type',
        ),
    ]
