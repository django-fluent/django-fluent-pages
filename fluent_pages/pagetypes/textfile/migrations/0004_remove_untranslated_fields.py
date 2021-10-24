from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("textfile", "0003_migrate_translatable_fields")]

    operations = [migrations.RemoveField(model_name="textfile", name="content")]
