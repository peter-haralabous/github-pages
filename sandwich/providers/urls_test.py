from http import HTTPStatus
from typing import Any

import pytest
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models import Encounter
from sandwich.core.models import Form
from sandwich.core.models import Invitation
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.role import RoleName
from sandwich.core.service.organization_service import assign_organization_role
from sandwich.core.urls_test import UrlRegistration
from sandwich.core.urls_test import get_all_urls
from sandwich.providers.urls import urlpatterns as providers_urlpatterns


def get_provider_urls() -> list[UrlRegistration]:
    return get_all_urls(providers_urlpatterns)


EXCLUDED_URL_NAMES = {
    # Redirects (not meaningful to GET test harness as they don't return 200 OK page content)
    "home",
    "organization",
    # POST-only endpoints (test harness only issues GET requests)
    "encounter_create",
    "form_file_upload",
    "patient_archive",
    "patient_add_task",
    "patient_resend_invite",
    "patient_cancel_task",
    "save_list_preference",
    "reset_list_preference",
    "save_organization_preference",
    "reset_organization_preference",
}


def test_no_stale_exclusions():
    assert EXCLUDED_URL_NAMES.issubset({url.name for url in get_provider_urls()})


@override_settings(FEATURE_PROVIDER_FORM_BUILDER=True)
@pytest.mark.parametrize("url", get_provider_urls(), ids=lambda url: url.name)
def test_provider_http_get_urls_return_status_200(db, user, organization, url) -> None:
    if url.name in EXCLUDED_URL_NAMES:
        pytest.skip(f"{url.name} is excluded")

    # Setup a provider-like user.
    assign_organization_role(organization, RoleName.OWNER, user)
    client = Client()
    client.force_login(user)

    # Need a patient in the org with an encounter
    patient = PatientFactory.create(organization=organization)
    encounter = Encounter.objects.create(
        patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
    )
    Invitation.objects.create(patient=patient, status=InvitationStatus.PENDING, token="")

    # Need a task for the task route
    task = TaskFactory.create(patient=patient, encounter=encounter)

    # Need an attribute definition for the attribute routes
    attribute = CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Test Date Attribute",
        data_type=CustomAttribute.DataType.DATE,
    )

    # Need a form for the form route
    form = Form.objects.create(organization=organization, name="Test Form", schema={"title": "Test Form"})

    kwargs: dict[str, Any] = {}

    if ":encounter_id>" in url.pattern:
        kwargs["encounter_id"] = encounter.pk
    if ":organization_id>" in url.pattern:
        kwargs["organization_id"] = organization.pk
    if ":patient_id>" in url.pattern:
        kwargs["patient_id"] = patient.pk
    if ":task_id>" in url.pattern:
        kwargs["task_id"] = task.pk
    if ":attribute_id>" in url.pattern:
        kwargs["attribute_id"] = attribute.pk
    if ":form_id>" in url.pattern:
        kwargs["form_id"] = form.pk
    if url.name in {"list_preference_settings", "organization_preference_settings_detail"}:
        kwargs["list_type"] = "encounter_list"

    response = client.get(reverse("providers:" + url.name, kwargs=kwargs))
    assert response.status_code == HTTPStatus.OK
