import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from playwright.sync_api import Page

from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import ListViewType
from sandwich.core.models import Organization
from sandwich.core.models.encounter import Encounter
from sandwich.core.service.list_preference_service import save_list_view_preference
from sandwich.users.models import User


@pytest.mark.e2e
@pytest.mark.django_db
def test_multiselect_widget_initializes_with_choices_js(  # noqa: PLR0915
    live_server, provider_page: Page, organization: Organization, provider: User, encounter: Encounter
) -> None:
    """Test that multiselect widgets are properly initialized with Choices.js."""
    content_type = ContentType.objects.get_for_model(Encounter)
    multi_attr = CustomAttribute.objects.create(
        organization=organization,
        name="multi-select",
        data_type=CustomAttribute.DataType.ENUM,
        is_multi=True,
        content_type=content_type,
    )
    option1 = CustomAttributeEnum.objects.create(
        attribute=multi_attr,
        label="Option 1",
        value="opt1",
        color_code="FF0000",
    )
    option2 = CustomAttributeEnum.objects.create(
        attribute=multi_attr,
        label="Option 2",
        value="opt2",
        color_code="00FF00",
    )
    option3 = CustomAttributeEnum.objects.create(
        attribute=multi_attr,
        label="Option 3",
        value="opt3",
        color_code="0000FF",
    )

    encounter.attributes.create(attribute=multi_attr, value_enum=option1)
    encounter.attributes.create(attribute=multi_attr, value_enum=option2)

    save_list_view_preference(
        organization=organization,
        list_type=ListViewType.ENCOUNTER_LIST,
        user=provider,
        visible_columns=["patient__first_name", "patient__last_name", "status", str(multi_attr.id)],
        saved_filters={},
    )

    url = f"{live_server.url}{reverse('providers:encounter_list', kwargs={'organization_id': organization.id})}"
    provider_page.goto(url)
    provider_page.wait_for_load_state("networkidle")

    table = provider_page.locator("table")
    assert table.is_visible(), "Encounter table should be visible"

    patient_link = provider_page.locator(
        f"text=/{encounter.patient.last_name}, {encounter.patient.first_name}/i"
    ).first
    if not patient_link.is_visible():
        msg = f"Patient {encounter.patient.first_name} {encounter.patient.last_name} not found in table"
        raise AssertionError(msg)

    row = patient_link.locator("xpath=ancestor::tr")

    multiselect_cell = row.locator("td").filter(has_text="Option 1").first
    multiselect_cell.wait_for(state="visible", timeout=5000)

    initial_text = multiselect_cell.text_content()
    assert initial_text is not None
    assert "Option 1" in initial_text, f"Expected 'Option 1' in cell but got: {initial_text}"
    encounter.refresh_from_db()
    attr_values = encounter.attributes.filter(attribute=multi_attr)
    saved_labels = [str(val.value_enum.label) for val in attr_values if val.value_enum]
    assert len(saved_labels) == 2, f"Expected 2 values saved, got {len(saved_labels)}: {saved_labels}"
    assert "Option 1" in saved_labels, "Expected 'Option 1' in saved values"
    assert "Option 2" in saved_labels, "Expected 'Option 2' in saved values"

    multiselect_cell.click()

    provider_page.wait_for_timeout(500)

    form_in_cell = multiselect_cell.locator("form")
    if form_in_cell.count() > 0:
        form_in_cell.locator("select[multiple]")
    else:
        pass

    choices_wrapper = row.locator(".choices")
    choices_wrapper.wait_for(state="visible", timeout=5000)

    assert choices_wrapper.is_visible(), "Choices.js wrapper should be visible"

    selected_badges = choices_wrapper.locator(".choices__item").filter(has_text="Remove item")
    badge_count = selected_badges.count()

    assert badge_count == 2, f"Expected 2 selected badges, got {badge_count}"

    badge_texts = selected_badges.all_text_contents()
    assert any("Option 1" in text for text in badge_texts), f"Expected 'Option 1' in badges: {badge_texts}"
    assert any("Option 2" in text for text in badge_texts), f"Expected 'Option 2' in badges: {badge_texts}"

    choices_inner = choices_wrapper.locator(".choices__inner")
    choices_inner.click()

    dropdown = provider_page.locator(".choices__list--dropdown")
    dropdown.wait_for(state="visible", timeout=2000)

    dropdown_items = dropdown.locator(".choices__item--choice")
    available_options = dropdown_items.all_text_contents()
    assert "Option 3" in available_options, f"Expected 'Option 3' in dropdown, got: {available_options}"

    option3_item = dropdown.locator(".choices__item--choice").filter(has_text="Option 3")
    option3_item.click()

    provider_page.wait_for_timeout(500)
    updated_badges = choices_wrapper.locator(".choices__item").filter(has_text="Remove item")
    assert updated_badges.count() == 3, f"Expected 3 selected badges after selection, got {updated_badges.count()}"

    updated_badge_texts = updated_badges.all_text_contents()
    assert any("Option 3" in text for text in updated_badge_texts), (
        f"Expected 'Option 3' badge after selection, got: {updated_badge_texts}"
    )

    form_element = form_in_cell
    form_element.dispatch_event("submit")

    provider_page.wait_for_timeout(1000)  # Give time for HTMX to process

    updated_cell = row.locator("td").filter(has_text="Option 1").first
    updated_cell.wait_for(state="visible", timeout=2000)
    updated_text = updated_cell.text_content()
    assert updated_text is not None
    assert "Option 1" in updated_text, f"Expected 'Option 1' in updated cell, got: {updated_text}"
    assert "Option 2" in updated_text, f"Expected 'Option 2' in updated cell, got: {updated_text}"
    assert "Option 3" in updated_text, f"Expected 'Option 3' in updated cell, got: {updated_text}"

    encounter.refresh_from_db()
    attr_values = encounter.attributes.filter(attribute=multi_attr)
    saved_enum_ids = [str(val.value_enum.id) for val in attr_values if val.value_enum]
    assert len(saved_enum_ids) == 3, f"Expected 3 values saved, got {len(saved_enum_ids)}"
    assert str(option1.id) in saved_enum_ids, f"Expected '{option1.id}' in saved values"
    assert str(option2.id) in saved_enum_ids, f"Expected '{option2.id}' in saved values"
    assert str(option3.id) in saved_enum_ids, f"Expected '{option3.id}' in saved values"
