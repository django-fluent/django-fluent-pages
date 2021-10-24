from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("fluent_pages", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="PlainTextFile",
            fields=[
                (
                    "urlnode_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        parent_link=True,
                        serialize=False,
                        primary_key=True,
                        to="fluent_pages.UrlNode",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("content", models.TextField(verbose_name="Contents")),
            ],
            options={
                "db_table": "pagetype_testapp_plaintextfile",
                "verbose_name_plural": "Plain text files",
                "verbose_name": "Plain text file",
            },
            bases=("fluent_pages.page",),
        ),
        migrations.CreateModel(
            name="SimpleTextPage",
            fields=[
                (
                    "urlnode_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        parent_link=True,
                        serialize=False,
                        primary_key=True,
                        to="fluent_pages.UrlNode",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("contents", models.TextField(verbose_name="Contents")),
            ],
            options={
                "db_table": "pagetype_testapp_simpletextpage",
                "verbose_name_plural": "Plain text pages",
                "verbose_name": "Plain text page",
            },
            bases=("fluent_pages.htmlpage",),
        ),
        migrations.CreateModel(
            name="ChildTypesPage",
            fields=[
                (
                    "urlnode_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        parent_link=True,
                        serialize=False,
                        primary_key=True,
                        to="fluent_pages.UrlNode",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("contents", models.TextField(verbose_name="Contents")),
            ],
            options={
                "db_table": "pagetype_testapp_childtypespage",
                "verbose_name_plural": "Plain text pages",
                "verbose_name": "Plain text page",
            },
            bases=("fluent_pages.htmlpage",),
        ),
        migrations.CreateModel(
            name="WebShopPage",
            fields=[
                (
                    "urlnode_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        parent_link=True,
                        serialize=False,
                        primary_key=True,
                        to="fluent_pages.UrlNode",
                        on_delete=models.CASCADE,
                    ),
                )
            ],
            options={
                "db_table": "pagetype_testapp_webshoppage",
                "verbose_name_plural": "Webshop pages",
                "verbose_name": "Webshop page",
            },
            bases=("fluent_pages.page",),
        ),
    ]
