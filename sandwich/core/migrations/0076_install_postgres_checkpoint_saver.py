from django.conf import settings
from django.db import migrations
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore


def install_postgres_checkpoint_saver(apps, schema_editor):
    with (
        PostgresSaver.from_conn_string(settings.DATABASE_URL) as checkpointer,
        PostgresStore.from_conn_string(settings.DATABASE_URL) as store,
    ):
        checkpointer.setup()
        store.setup()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0075_backfill_completed_form_submissions"),
    ]

    operations = [
        migrations.RunPython(
            install_postgres_checkpoint_saver,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
