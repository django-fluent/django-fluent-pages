import parler.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("textfile", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="TextFileTranslation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "language_code",
                    models.CharField(max_length=15, verbose_name="Language", db_index=True),
                ),
                ("content", models.TextField(verbose_name="File contents")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        related_name="text_translations",
                        editable=False,
                        to="textfile.TextFile",
                        on_delete=models.CASCADE,
                        null=True,
                    ),
                ),
            ],
            options={
                "managed": True,
                "db_table": "textfile_textfile_translation",
                "db_tablespace": "",
                "default_permissions": (),
                "verbose_name": "Plain text file Translation",
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="textfiletranslation",
            unique_together={("language_code", "master")},
        ),
    ]
