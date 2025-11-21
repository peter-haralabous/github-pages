from http import HTTPStatus
from typing import Any

import pytest
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.summary import SummaryFactory
from sandwich.core.factories.summary_template import SummaryTemplateFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models import Encounter
from sandwich.core.models import Form
from sandwich.core.models import Invitation
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.role import RoleName
from sandwich.core.models.summary import SummaryStatus
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
    "encounter_archive",
    "form_file_upload",
    "patient_add_task",
    "patient_resend_invite",
    "patient_cancel_task",
    "save_list_preference",
    "reset_list_preference",
    "save_organization_preference",
    "reset_organization_preference",
    "apply_filter",
    "remove_filter",
    "clear_all_filters",
    "save_current_filters",
    # GET endpoints that require query parameters we can't easily provide
    "get_filter_options",
    "get_filter_options_with_id",
    # Ninja api routes below,
    "providers-api:api-root",
    "providers-api:openapi-json",
    "providers-api:openapi-view",
    "providers-api:save_form",
}


def test_no_stale_exclusions():
    unknown = EXCLUDED_URL_NAMES - {url.name for url in get_provider_urls()}
    assert unknown == set()


def _build_url_kwargs(url: UrlRegistration, test_objects: dict[str, Any]) -> dict[str, Any]:  # noqa: C901
    """Build kwargs dict for URL reverse lookup based on URL pattern and name."""
    kwargs: dict[str, Any] = {}

    if ":encounter_id>" in url.pattern:
        kwargs["encounter_id"] = test_objects["encounter"].pk
    if ":organization_id>" in url.pattern:
        kwargs["organization_id"] = test_objects["organization"].pk
    if ":patient_id>" in url.pattern:
        kwargs["patient_id"] = test_objects["patient"].pk
    if ":task_id>" in url.pattern:
        kwargs["task_id"] = test_objects["task"].pk
    if ":attribute_id>" in url.pattern:
        kwargs["attribute_id"] = test_objects["attribute"].pk
    if ":form_id>" in url.pattern:
        kwargs["form_id"] = test_objects["form"].pk
    if ":form_version_id>" in url.pattern:
        kwargs["form_version_id"] = test_objects["form"].get_current_version().pgh_id
    if ":template_id>" in url.pattern:
        kwargs["template_id"] = test_objects["template"].pk
    if ":summary_id>" in url.pattern:
        kwargs["summary_id"] = test_objects["summary"].pk
    if url.name in {
        "list_preference_settings",
        "organization_preference_settings_detail",
        "show_filter_modal",
        "apply_filter",
        "remove_filter",
        "clear_all_filters",
        "save_current_filters",
    }:
        kwargs["list_type"] = "encounter_list"
    if ":field_id>" in url.pattern:
        kwargs["field_id"] = "status"
    if ":field_name>" in url.pattern:
        kwargs["field_name"] = "status"

    return kwargs


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

    # Need a summary template for the summary template routes
    template = SummaryTemplateFactory.create(organization=organization, form=form)

    # Need a summary for the summary detail route
    summary = SummaryFactory.create(
        patient=patient, organization=organization, encounter=encounter, status=SummaryStatus.SUCCEEDED
    )

    test_objects = {
        "encounter": encounter,
        "organization": organization,
        "patient": patient,
        "task": task,
        "attribute": attribute,
        "form": form,
        "template": template,
        "summary": summary,
    }
    kwargs = _build_url_kwargs(url, test_objects)

    response = client.get(reverse("providers:" + url.name, kwargs=kwargs), follow=True)
    assert response.status_code == HTTPStatus.OK
