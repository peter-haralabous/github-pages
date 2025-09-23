from uuid import uuid4

from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(TimestampedModel, UUIDModel):
    class Meta:
        abstract = True


# TODO: add a common soft-delete model
#       could use or copy from django-softdelete or django-model-utils
