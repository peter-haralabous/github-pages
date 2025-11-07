import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Document
from sandwich.core.models import Patient


def test_document_download(client, user, patient: Patient):
    client.force_login(user)

    document = Document.objects.create(patient=patient, file=SimpleUploadedFile(name="empty", content=b""))

    url = reverse("patients:document_download", kwargs={"document_id": document.pk})
    response = client.get(url)
    assert response.status_code == 200


def test_document_download_as_another_user(client, user, patient: Patient):
    client.force_login(user)

    another_patient = PatientFactory.create()
    document = Document.objects.create(patient=another_patient, file=SimpleUploadedFile(name="empty", content=b""))

    url = reverse("patients:document_download", kwargs={"document_id": document.pk})
    response = client.get(url)
    assert response.status_code == 404


def test_document_upload_and_extract(client, user, patient: Patient):
    client.force_login(user)

    url = reverse("patients:document_upload_and_extract", kwargs={"patient_id": patient.pk})
    pdf_content = b"%PDF-1.4 test pdf file"
    file = SimpleUploadedFile("testfile.pdf", pdf_content, content_type="application/pdf")
    response = client.post(url, {"file": file})
    assert response.status_code == 200

    document = Document.objects.get(patient=patient)
    assert document.content_type == "application/pdf"
    assert document.size == len(pdf_content)
    assert document.original_filename == "testfile.pdf"

    assert user.has_perm("view_document", document)
    assert user.has_perm("change_document", document)
    assert user.has_perm("delete_document", document)


def test_document_upload_and_extract_multiple(client, user, patient: Patient):
    client.force_login(user)

    url = reverse("patients:document_upload_and_extract", kwargs={"patient_id": patient.pk})
    pdf_content = b"%PDF-1.4 test pdf file"
    file1 = SimpleUploadedFile("file1.pdf", pdf_content, content_type="application/pdf")
    file2 = SimpleUploadedFile("file2.pdf", pdf_content, content_type="application/pdf")
    response = client.post(url, {"file": [file1, file2]})
    assert response.status_code == 200

    assert Document.objects.filter(patient=patient).count() == 2


def test_document_upload_and_extract_deny_access(client, user, patient: Patient):
    client.force_login(user)
    random_patient = PatientFactory.create()

    url = reverse("patients:document_upload_and_extract", kwargs={"patient_id": random_patient.pk})
    pdf_content = b"%PDF-1.4 test pdf file"
    file = SimpleUploadedFile("testfile.pdf", pdf_content, content_type="application/pdf")
    response = client.post(url, {"file": file})
    assert response.status_code == 404

    with pytest.raises(Document.DoesNotExist):
        Document.objects.get(patient=random_patient)


def test_document_delete(client: Client, user, patient: Patient):
    document = Document.objects.create(patient=patient, file=SimpleUploadedFile(name="empty", content=b""))

    client.force_login(user)
    url = reverse("patients:document_delete", kwargs={"patient_id": patient.id, "document_id": document.id})
    response = client.post(url)

    assert response.status_code == 200
    with pytest.raises(Document.DoesNotExist):
        Document.objects.get(patient=patient)


def test_document_delete_deny_access(client: Client, user, patient: Patient):
    random_patient = PatientFactory.create()
    document = Document.objects.create(patient=random_patient, file=SimpleUploadedFile(name="empty", content=b""))

    client.force_login(user)
    url = reverse("patients:document_delete", kwargs={"patient_id": random_patient.id, "document_id": document.id})
    response = client.post(url)

    assert response.status_code == 404
    assert Document.objects.get(id=document.id)
