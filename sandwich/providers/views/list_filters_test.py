import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.models import ListViewPreference
from sandwich.core.models import ListViewType
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.service.list_preference_service import save_list_view_preference


@pytest.mark.django_db
def test_save_filters_materializes_user_preference_and_persists_filters(
    provider,
    organization,
):
    client = Client()
    client.force_login(provider)

    assert not ListViewPreference.objects.filter(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
    ).exists()

    url = reverse(
        "providers:save_current_filters",
        kwargs={
            "organization_id": organization.id,
            "list_type": ListViewType.ENCOUNTER_LIST.value,
        },
    )

    response = client.post(
        f"{url}?filter_status={EncounterStatus.IN_PROGRESS.value}&filter_mode=custom",
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert response["HX-Redirect"]
    assert "filter_mode" not in response["HX-Redirect"]

    preference = ListViewPreference.objects.get(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
    )

    assert preference.saved_filters == {
        "custom_attributes": {},
        "model_fields": {"status": EncounterStatus.IN_PROGRESS.value},
    }


@pytest.mark.django_db
def test_clear_all_filters_sets_custom_mode(provider, organization):
    client = Client()
    client.force_login(provider)

    url = reverse(
        "providers:clear_all_filters",
        kwargs={
            "organization_id": organization.id,
            "list_type": ListViewType.ENCOUNTER_LIST.value,
        },
    )

    response = client.post(
        f"{url}?filter_status={EncounterStatus.IN_PROGRESS.value}",
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "filter_mode=custom" in response["HX-Redirect"]
    assert "filter_status" not in response["HX-Redirect"]


@pytest.mark.django_db
def test_custom_mode_prevents_saved_filters_from_applying(provider, organization):
    save_list_view_preference(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
        visible_columns=["patient__first_name"],
        saved_filters={
            "model_fields": {"status": EncounterStatus.IN_PROGRESS.value},
            "custom_attributes": {},
        },
    )

    client = Client()
    client.force_login(provider)
    url = reverse("providers:encounter_list", kwargs={"organization_id": organization.id})

    # With filter_mode=custom, saved filters should not apply
    response = client.get(f"{url}?filter_mode=custom")

    assert response.status_code == 200
    assert "filter_status" not in response.request["QUERY_STRING"]


@pytest.mark.django_db
def test_apply_filter_sets_custom_mode(provider, organization):
    client = Client()
    client.force_login(provider)

    url = reverse(
        "providers:apply_filter",
        kwargs={
            "organization_id": organization.id,
            "list_type": ListViewType.ENCOUNTER_LIST.value,
        },
    )

    response = client.post(
        url,
        {
            "field_id": "status",
            "values": [EncounterStatus.IN_PROGRESS.value],
        },
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "filter_mode=custom" in response["HX-Redirect"]


@pytest.mark.django_db
def test_remove_filter_sets_custom_mode(provider, organization):
    """Test that removing a filter sets custom mode."""
    client = Client()
    client.force_login(provider)

    url = reverse(
        "providers:remove_filter",
        kwargs={
            "organization_id": organization.id,
            "list_type": ListViewType.ENCOUNTER_LIST.value,
            "field_id": "status",
        },
    )

    response = client.post(
        f"{url}?filter_status={EncounterStatus.IN_PROGRESS.value}",
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert "filter_mode=custom" in response["HX-Redirect"]
    assert "filter_status" not in response["HX-Redirect"]


@pytest.mark.django_db
def test_can_save_empty_filters_after_clear_all(provider, organization):
    """Test that user can save empty filter set after clearing all filters."""
    # First save some filters
    save_list_view_preference(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
        visible_columns=["patient__first_name"],
        saved_filters={
            "model_fields": {"status": EncounterStatus.IN_PROGRESS.value},
            "custom_attributes": {},
        },
    )

    client = Client()
    client.force_login(provider)

    clear_url = reverse(
        "providers:clear_all_filters",
        kwargs={
            "organization_id": organization.id,
            "list_type": ListViewType.ENCOUNTER_LIST.value,
        },
    )
    response = client.post(
        f"{clear_url}?filter_status={EncounterStatus.IN_PROGRESS.value}",
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert "filter_mode=custom" in response["HX-Redirect"]

    # Now save the empty filter set
    save_url = reverse(
        "providers:save_current_filters",
        kwargs={
            "organization_id": organization.id,
            "list_type": ListViewType.ENCOUNTER_LIST.value,
        },
    )
    response = client.post(
        f"{save_url}?filter_mode=custom",
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert response["HX-Redirect"]

    # Verify empty filters were saved
    preference = ListViewPreference.objects.get(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
    )
    assert preference.saved_filters == {"custom_attributes": {}, "model_fields": {}}
