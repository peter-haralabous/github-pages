import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from sandwich.core.models.attachment import Attachment
from sandwich.users.models import User


@pytest.mark.django_db
def test_attachment_upload(user: User):
    uploaded_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")

    url = reverse("core:attachment_upload")
    client = Client()
    client.force_login(user)
    response = client.post(url, {"file-upload": uploaded_file})

    assert response.status_code == 200
    data = json.loads(response.content)

    assert data["original_filename"] == "test.txt"
    assert data["content_type"] == "text/plain"
    assert "id" in data
    assert "url" in data

    attachment = Attachment.objects.get(pk=data["id"])
    assert attachment.uploaded_by == user


@pytest.mark.django_db
def test_attachment_delete(user: User):
    attachment = Attachment.objects.create(
        uploaded_by=user,
        original_filename="to_delete.txt",
        file=SimpleUploadedFile("to_delete.txt", b"delete me"),
    )

    url = reverse("core:attachment_delete", kwargs={"attachment_id": attachment.id})
    client = Client()
    client.force_login(user)

    response = client.delete(url)

    assert response.status_code == 204
    assert not Attachment.objects.filter(pk=attachment.pk).exists()


@pytest.mark.django_db
def test_attachment_get_by_id(user: User) -> None:
    attachment = Attachment.objects.create(
        uploaded_by=user,
        original_filename="fetch_me.txt",
        file=SimpleUploadedFile("fetch_me.txt", b"fetch me"),
    )

    url = reverse("core:attachment_by_id", kwargs={"attachment_id": attachment.id})
    client = Client()
    client.force_login(user)
    response = client.get(url)

    data = json.loads(response.content)
    assert "url" in data
    assert data["url"] == attachment.file.url
