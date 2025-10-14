from http import HTTPStatus

from django.test import Client
from django.urls import URLPattern
from django.urls import URLResolver
from django.urls import reverse

from sandwich.core.factories import PatientFactory
from sandwich.core.urls_test import get_all_urls
from sandwich.patients.urls import urlpatterns as patients_urlspatterns


def get_patient_urls() -> list[URLPattern | URLResolver]:
    return get_all_urls(patients_urlspatterns)  # type: ignore[arg-type]


def test_patient_http_get_urls_return_status_200(db, user) -> None:
    patient = PatientFactory.create(user=user)
    client = Client()
    client.force_login(user)

    # List of urls which are other http verbs (e.g. POST) or redirect (non HTTP 200)
    exclude_url_names = [
        "home",  # Redirect
        "accept_invite",  # POST
        "document_delete",  # POST
        "document_upload",  # POST
        "task",  # POST
        "api-root",  # Ninja api routes below
        "openapi-json",
        "openapi-view",
        "get_formio_form",  # see formio.py
        "get_formio_form_submission",
        "list_formio_form_submissions",
        "submit_formio_form",
        "update_formio_form_submission_with_id",
        "update_formio_form_submission_without_id",
    ]

    patient_urls = get_patient_urls()
    found_patient_route_names = {
        obj.get("name")  # type: ignore[union-attr]
        for obj in patient_urls
        if obj.get("name") and obj.get("name") not in exclude_url_names  # type: ignore[union-attr]
    }

    urls = [
        (reverse("patients:patient_add"), "patient_add"),
        (reverse("patients:patient_onboarding_add"), "patient_onboarding_add"),
        (reverse("patients:patient_details", kwargs={"patient_id": patient.pk}), "patient_details"),
        (reverse("patients:patient_edit", kwargs={"patient_id": patient.pk}), "patient_edit"),
    ]

    tested_patient_route_names = set()
    for url, url_name in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, f"URL {url_name} returned {response.status_code}"
        tested_patient_route_names.add(url_name)

    assert found_patient_route_names == tested_patient_route_names
