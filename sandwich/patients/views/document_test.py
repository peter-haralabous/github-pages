from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
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


def test_document_upload(client, user):
    client.force_login(user)
    patient = PatientFactory.create(user=user)

    url = reverse("patients:document_upload", kwargs={"patient_id": patient.pk})
    pdf_content = b"%PDF-1.4 test pdf file"
    file = SimpleUploadedFile("testfile.pdf", pdf_content, content_type="application/pdf")
    response = client.post(url, {"file": file})
    assert response.status_code == 200

    document = Document.objects.get(patient=patient)
    assert document.content_type == "application/pdf"
    assert document.size == len(pdf_content)
    assert document.original_filename == "testfile.pdf"
