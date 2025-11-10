from http import HTTPStatus

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.fact import FactFactory
from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Entity
from sandwich.core.models import Immunization
from sandwich.core.models import Practitioner
from sandwich.core.models.entity import EntityType
from sandwich.core.models.predicate import PredicateName
from sandwich.core.service.entity_service import entity_for_patient
from sandwich.core.service.predicate_service import predicate_for_predicate_name
from sandwich.core.urls_test import UrlRegistration
from sandwich.core.urls_test import get_all_urls
from sandwich.patients.urls import urlpatterns as patients_urlspatterns


def get_patient_urls() -> list[UrlRegistration]:
    return get_all_urls(patients_urlspatterns)


# List of urls which are other http verbs (e.g. POST) or redirect (non HTTP 200)
EXCLUDED_URL_NAMES = {
    "home",  # Redirect
    "accept_invite",  # POST
    "chat",  # POST
    "document_delete",  # POST
    "document_upload_and_extract",  # POST
    "task",  # POST
    "patient_onboarding_add",  # redirects if there's already a patient for the user
    "health_records_add",  # needs record type in the url; covered in `health_records_test.py`
    # Ninja api routes below
    "api-1.0.0:api-root",
    "api-1.0.0:openapi-json",
    "api-1.0.0:openapi-view",
    "api-1.0.0:get_formio_form",
    "api-1.0.0:get_formio_form_submission",
    "api-1.0.0:list_formio_form_submissions",
    "api-1.0.0:save_draft_form",
    "api-1.0.0:submit_formio_form",
    "api-1.0.0:submit_form",
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

    if ":condition_id>" in url.pattern:
        kwargs["condition_id"] = Condition.objects.create(patient=patient).pk

    if ":document_id>" in url.pattern:
        kwargs["document_id"] = Document.objects.create(
            patient=patient, file=SimpleUploadedFile(name="empty", content=b"")
        ).pk

    if ":fact_id>" in url.pattern:
        kwargs["fact_id"] = FactFactory.create(
            patient=patient,
            subject=entity_for_patient(patient),
            predicate=predicate_for_predicate_name(PredicateName.HAS_SYMPTOM),
            object=Entity.objects.create(type=EntityType.OBSERVATION),
        ).pk

    if ":immunization_id>" in url.pattern:
        kwargs["immunization_id"] = Immunization.objects.create(
            patient=patient,
            name="test",
            date="2022-01-01",
        ).pk

    if ":practitioner_id>" in url.pattern:
        kwargs["practitioner_id"] = Practitioner.objects.create(
            patient=patient,
            name="Dr. Chris Brendlinger",
        ).pk

    if ":task_id>" in url.pattern or "<task_id>" in url.pattern:
        # create a small form and a task for this patient so the task-based
        # endpoints resolve and return 200
        form = FormFactory.create(name="URL Test Form", schema={"elements": []}, organization=patient.organization)
        task = TaskFactory.create(patient=patient, form_version=form.events.last())
        kwargs["task_id"] = task.pk

    response = client.get(reverse("patients:" + url.name, kwargs=kwargs))
    assert response.status_code == HTTPStatus.OK
