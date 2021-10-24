from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("fluent_pages", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="FluentPage",
            fields=[
                (
                    "urlnode_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="fluent_pages.UrlNode",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "layout",
                    models.ForeignKey(
                        verbose_name="Layout",
                        to="fluent_pages.PageLayout",
                        on_delete=models.CASCADE,
                        null=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "db_table": "pagetype_fluentpage_fluentpage",
                "verbose_name": "Page",
                "verbose_name_plural": "Pages",
                "permissions": (("change_page_layout", "Can change Page layout"),),
            },
            bases=("fluent_pages.htmlpage",),
        )
    ]
