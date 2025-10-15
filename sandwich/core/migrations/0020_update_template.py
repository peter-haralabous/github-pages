from django.core.management import call_command
from django.db import migrations


def load_initial_data(apps, schema_editor):
    call_command("loaddata", "sandwich/core/migrations/fixtures/0020_template.json")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0019_alter_document_encounter"),
    ]

    operations = [
        migrations.RunPython(load_initial_data, reverse_code=migrations.RunPython.noop),
    ]
