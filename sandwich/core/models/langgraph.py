"""

These are **Unmanaged** Django models for the LangGraph-related database tables.

See:
  - https://docs.langchain.com/oss/python/langgraph/add-memory
  - https://docs.djangoproject.com/en/stable/ref/django-admin/#inspectdb
  - https://docs.djangoproject.com/en/stable/ref/models/options/#django.db.models.Options.managed
  - sandwich/core/migrations/0076_install_postgres_checkpoint_saver.py

"""

from django.db import models


class Checkpoints(models.Model):
    pk = models.CompositePrimaryKey("thread_id", "checkpoint_ns", "checkpoint_id")
    thread_id = models.TextField()
    checkpoint_ns = models.TextField()
    checkpoint_id = models.TextField()
    parent_checkpoint_id = models.TextField(blank=True, null=True)  # noqa: DJ001
    type = models.TextField(blank=True, null=True)  # noqa: DJ001
    checkpoint = models.JSONField()
    metadata = models.JSONField()

    class Meta:
        managed = False
        db_table = "checkpoints"

    def __str__(self):
        return f"Checkpoint({self.pk=})"


class CheckpointBlobs(models.Model):
    pk = models.CompositePrimaryKey("thread_id", "checkpoint_ns", "channel", "version")
    thread_id = models.TextField()
    checkpoint_ns = models.TextField()
    channel = models.TextField()
    version = models.TextField()
    type = models.TextField()
    blob = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "checkpoint_blobs"

    def __str__(self):
        return f"CheckpointBlob({self.pk=})"


class CheckpointWrites(models.Model):
    pk = models.CompositePrimaryKey("thread_id", "checkpoint_ns", "checkpoint_id", "task_id", "idx")
    thread_id = models.TextField()
    checkpoint_ns = models.TextField()
    checkpoint_id = models.TextField()
    task_id = models.TextField()
    idx = models.IntegerField()
    channel = models.TextField()
    type = models.TextField(blank=True, null=True)  # noqa: DJ001
    blob = models.BinaryField()
    task_path = models.TextField()

    class Meta:
        managed = False
        db_table = "checkpoint_writes"

    def __str__(self):
        return f"CheckpointWrite({self.pk=})"


class CheckpointMigrations(models.Model):
    v = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = "checkpoint_migrations"

    def __str__(self):
        return f"CheckpointMigrations(v={self.v})"


class Store(models.Model):
    pk = models.CompositePrimaryKey("prefix", "key")
    prefix = models.TextField()
    key = models.TextField()
    value = models.JSONField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    ttl_minutes = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "store"

    def __str__(self):
        return f"Store({self.pk=})"


class StoreMigrations(models.Model):
    v = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = "store_migrations"

    def __str__(self):
        return f"StoreMigrations(v={self.v})"
