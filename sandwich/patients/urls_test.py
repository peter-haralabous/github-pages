from http import HTTPStatus

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from sandwich.core.models import Document
from sandwich.core.urls_test import UrlRegistration
from sandwich.core.urls_test import get_all_urls
from sandwich.patients.urls import urlpatterns as patients_urlspatterns


def get_patient_urls() -> list[UrlRegistration]:
    return get_all_urls(patients_urlspatterns)


# List of urls which are other http verbs (e.g. POST) or redirect (non HTTP 200)
EXCLUDED_URL_NAMES = {
    "home",  # Redirect
    "accept_invite",  # POST
    "document_delete",  # POST
    "document_upload_and_extract",  # POST
    "task",  # POST
    # Ninja api routes below
    "api-1.0.0:api-root",
    "api-1.0.0:openapi-json",
    "api-1.0.0:openapi-view",
    "api-1.0.0:get_formio_form",
    "api-1.0.0:get_formio_form_submission",
    "api-1.0.0:list_formio_form_submissions",
    "api-1.0.0:submit_formio_form",
    "api-1.0.0:update_formio_form_submission_with_id",
    "api-1.0.0:update_formio_form_submission_without_id",
}


def test_no_stale_exclusions():
    assert EXCLUDED_URL_NAMES.issubset({url.name for url in get_patient_urls()})


@pytest.mark.parametrize("url", get_patient_urls(), ids=lambda url: url.name)
def test_patient_http_get_urls_return_status_200(db, user, url, patient) -> None:
    if url.name in EXCLUDED_URL_NAMES:
        pytest.skip(f"{url.name} is excluded")

    client = Client()
    client.force_login(user)
    kwargs = {}

    if ":patient_id>" in url.pattern:
        kwargs["patient_id"] = patient.pk

    if ":document_id>" in url.pattern:
        kwargs["document_id"] = Document.objects.create(
            patient=patient, file=SimpleUploadedFile(name="empty", content=b"")
        ).pk

    response = client.get(reverse("patients:" + url.name, kwargs=kwargs))
    assert response.status_code == HTTPStatus.OK
