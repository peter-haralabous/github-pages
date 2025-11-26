from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from sandwich.core.models.attachment import Attachment
from sandwich.users.models import User


def test_attachment_create_assigns_permissions(user: User) -> None:
    # test for assign_default_attachment_permissions can be found in
    # sandwich/core/service/attachment_service_test.py
    with patch("sandwich.core.service.attachment_service.assign_default_attachment_permissions") as mock_create:
        created = Attachment.objects.create(uploaded_by=user, file=SimpleUploadedFile(name="test", content=b""))
        mock_create.assert_called_once_with(created)
