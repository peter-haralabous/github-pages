from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from sandwich.core.factories import PatientFactory
from sandwich.core.models import Document


def test_document_download(client, user):
    client.force_login(user)
    patient = PatientFactory.create(user=user)

    document = Document.objects.create(patient=patient, file=SimpleUploadedFile(name="empty", content=b""))

    url = reverse("patients:document_download", kwargs={"document_id": document.pk})
    response = client.get(url)
    assert response.status_code == 200


def test_document_download_as_another_user(client, user):
    client.force_login(user)
    PatientFactory.create(user=user)

    another_patient = PatientFactory.create()
    document = Document.objects.create(patient=another_patient, file=SimpleUploadedFile(name="empty", content=b""))

    url = reverse("patients:document_download", kwargs={"document_id": document.pk})
    response = client.get(url)
    assert response.status_code == 404
