# Generated by Django 3.2.18 on 2023-02-27 12:16

from django.db import migrations, models
import django.db.models.deletion
import parler.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_pages', '0005_author_on_delete_set_null'),
    ]

    operations = [
        # As defined in django-mptt >= 0.10.0
        migrations.AlterField(
            model_name='urlnode',
            name='level',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='urlnode',
            name='lft',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='urlnode',
            name='rght',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]