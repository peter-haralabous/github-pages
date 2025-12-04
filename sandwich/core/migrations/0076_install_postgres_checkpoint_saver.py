from contextlib import contextmanager

from django.db import migrations
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg.rows import dict_row

# NOTE-NG: we override the default langgraph postgres backends to avoid `binary=True` on the cursors that it creates.
# This avoids the following error:
# > psycopg.NotSupportedError: client-side cursors don't support binary results


class CustomPostgresSaver(PostgresSaver):
    @contextmanager
    def _cursor(self, *, pipeline: bool = False):
        assert not pipeline, "Pipeline mode is not supported."
        with self.lock, self.conn as conn, conn.cursor(row_factory=dict_row) as cursor:
            yield cursor


class CustomPostgresStore(PostgresStore):
    @contextmanager
    def _cursor(self, *, pipeline: bool = False):
        assert not pipeline, "Pipeline mode is not supported."
        with self.conn as conn, conn.cursor(row_factory=dict_row) as cursor:
            yield cursor


def install_postgres_checkpoint_saver(apps, schema_editor):
    connection = schema_editor.connection.connection
    CustomPostgresSaver(connection).setup()
    CustomPostgresStore(connection).setup()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("core", "0075_backfill_completed_form_submissions"),
    ]

    operations = [
        migrations.RunPython(
            install_postgres_checkpoint_saver,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
