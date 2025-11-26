from django.db import models
from private_storage.fields import PrivateFileField

from sandwich.core.models.abstract import BaseModel
from sandwich.users.models import User


class AttachmentManager(models.Manager["Attachment"]):
    def create(self, **kwargs) -> "Attachment":
        from sandwich.core.service.attachment_service import assign_default_attachment_permissions  # noqa: PLC0415

        attachment = super().create(**kwargs)
        assign_default_attachment_permissions(attachment)
        return attachment


class Attachment(BaseModel):
    file = PrivateFileField(upload_to="attachments/")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # metadata about the uploaded file
    content_type = models.CharField(max_length=255, blank=True)
    size = models.BigIntegerField(null=True, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)

    objects = AttachmentManager()

    def __str__(self) -> str:
        return self.original_filename
