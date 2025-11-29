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

    assert len(data) == 1
    item = data[0]
    assert item["original_filename"] == "test.txt"
    assert item["content_type"] == "text/plain"
    assert "id" in item
    assert "url" in item

    attachment = Attachment.objects.get(pk=item["id"])
    assert attachment.uploaded_by == user


@pytest.mark.django_db
def test_attachment_upload_supports_multiple_files(user: User):
    uploaded_files = [
        SimpleUploadedFile("test1.txt", b"test content 1", content_type="text/plain"),
        SimpleUploadedFile("test2.txt", b"test content 2", content_type="text/plain"),
    ]

    url = reverse("core:attachment_upload")
    client = Client()
    client.force_login(user)
    response = client.post(url, {"file-upload": uploaded_files})

    assert response.status_code == 200
    data = json.loads(response.content)

    assert len(data) == 2
    filenames = {item["original_filename"] for item in data}
    assert filenames == {"test1.txt", "test2.txt"}

    for item in data:
        assert item["content_type"] == "text/plain"
        assert "id" in item
        assert "url" in item
        attachment = Attachment.objects.get(pk=item["id"])
        assert attachment.uploaded_by == user


@pytest.mark.django_db
def test_attachment_delete(user: User):
    attachment = Attachment.objects.create(
        uploaded_by=user,
        original_filename="to_delete.txt",
        file=SimpleUploadedFile("to_delete.txt", b"delete me"),
    )

    url = reverse("core:attachment_delete", query={"name": attachment.original_filename})
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

    url = reverse("core:attachment_by_name", query={"name": attachment.original_filename})
    client = Client()
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200
    assert response.content == b"fetch me"
    assert response["Content-Disposition"] == 'inline; filename="fetch_me.txt"'
