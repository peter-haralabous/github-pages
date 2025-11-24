import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from playwright.sync_api import Page

from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.organization import Organization


@pytest.mark.e2e
@pytest.mark.django_db
def test_edit_custom_attribute(live_server, owner_page: Page, organization: Organization):
    attribute = CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Priority",
        data_type=CustomAttribute.DataType.ENUM,
        is_multi=False,
    )

    enum_value = CustomAttributeEnum.objects.create(
        attribute=attribute,
        label="High Priority",
        value="high",
        color_code="FF0000",
    )

    url = f"{live_server.url}{
        reverse(
            'providers:custom_attribute_edit',
            kwargs={'organization_id': organization.id, 'attribute_id': attribute.id},
        )
    }"
    owner_page.goto(url)
    owner_page.wait_for_load_state("networkidle")

    attribute_form = owner_page.locator("#custom-attribute-form")
    assert attribute_form.is_visible()

    name_field = owner_page.locator("#id_name")
    name_field.click()
    name_field.type("Edit Test")

    enum_form = owner_page.locator("[data-enum-formset]")
    assert enum_form.is_visible()

    name_field = owner_page.locator("#id_enums-0-label")
    name_field.click()
    name_field.type("Edit Test")

    submit_button = owner_page.locator("button[type='submit']", has_text="Submit")
    submit_button.click()

    updated_attribute = CustomAttribute.objects.filter(id=attribute.id).first()
    assert updated_attribute
    assert str(updated_attribute.name).__contains__("Edit Test")

    updated_enum = CustomAttributeEnum.objects.filter(id=enum_value.id).first()
    assert updated_enum
    assert str(updated_enum.label).__contains__("Edit Test")


@pytest.mark.e2e
@pytest.mark.django_db
def test_remove_custom_enum(live_server, owner_page: Page, organization: Organization):
    attribute = CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Priority",
        data_type=CustomAttribute.DataType.ENUM,
        is_multi=False,
    )

    CustomAttributeEnum.objects.create(
        attribute=attribute,
        label="High Priority",
        value="high",
        color_code="FF0000",
    )

    CustomAttributeEnum.objects.create(
        attribute=attribute,
        label="Low Priority",
        value="low",
        color_code="FFFF00",
    )

    url = f"{live_server.url}{
        reverse(
            'providers:custom_attribute_edit',
            kwargs={'organization_id': organization.id, 'attribute_id': attribute.id},
        )
    }"
    owner_page.goto(url)
    owner_page.wait_for_load_state("networkidle")

    enum_form = owner_page.locator("[data-enum-formset]")
    assert enum_form.is_visible()

    owner_page.locator("button.delete-option-btn").first.click()

    submit_button = owner_page.locator("button[type='submit']", has_text="Submit")
    submit_button.click()

    reamining_enums = CustomAttributeEnum.objects.filter(attribute=attribute.id).count()
    assert reamining_enums == 1


@pytest.mark.e2e
@pytest.mark.django_db
def test_add_custom_enum(live_server, owner_page: Page, organization: Organization):
    attribute = CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Priority",
        data_type=CustomAttribute.DataType.ENUM,
        is_multi=False,
    )

    CustomAttributeEnum.objects.create(
        attribute=attribute,
        label="High Priority",
        value="high",
        color_code="FF0000",
    )

    url = f"{live_server.url}{
        reverse(
            'providers:custom_attribute_edit',
            kwargs={'organization_id': organization.id, 'attribute_id': attribute.id},
        )
    }"
    owner_page.goto(url)
    owner_page.wait_for_load_state("networkidle")

    enum_form = owner_page.locator("[data-enum-formset]")
    assert enum_form.is_visible()

    owner_page.locator("#add-option-btn").click()

    name_field = owner_page.locator("#id_enums-1-label")
    name_field.click()
    name_field.type("Low Priority")

    name_field = owner_page.locator("#id_enums-1-value")
    name_field.click()
    name_field.type("low")

    name_field = owner_page.locator("#id_enums-1-color_code")
    name_field.click()
    name_field.type("00FF00")

    submit_button = owner_page.locator("button[type='submit']", has_text="Submit")
    submit_button.click()

    reamining_enums = CustomAttributeEnum.objects.filter(attribute=attribute.id).count()
    assert reamining_enums == 2


@pytest.mark.e2e
@pytest.mark.django_db
def test_edit_custom_attribute_validation(live_server, owner_page: Page, organization: Organization):
    attribute = CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Priority",
        data_type=CustomAttribute.DataType.ENUM,
        is_multi=False,
    )

    CustomAttributeEnum.objects.create(
        attribute=attribute,
        label="High Priority",
        value="high",
        color_code="FF0000",
    )

    url = f"{live_server.url}{
        reverse(
            'providers:custom_attribute_edit',
            kwargs={'organization_id': organization.id, 'attribute_id': attribute.id},
        )
    }"
    owner_page.goto(url)
    owner_page.wait_for_load_state("networkidle")

    enum_form = owner_page.locator("[data-enum-formset]")
    assert enum_form.is_visible()

    # Remove all option and test validation
    owner_page.locator("button.delete-option-btn").first.click()

    submit_button = owner_page.locator("button[type='submit']", has_text="Submit")
    submit_button.click()

    type_error = owner_page.locator("#error_1_id_input_type")
    assert type_error.is_visible()

    # Add new option and verify that forms save, but only latest option exists
    owner_page.locator("#add-option-btn").click()

    name_field = owner_page.locator("#id_enums-1-label")
    name_field.click()
    name_field.type("Low Priority")

    name_field = owner_page.locator("#id_enums-1-value")
    name_field.click()
    name_field.type("low")

    name_field = owner_page.locator("#id_enums-1-color_code")
    name_field.click()
    name_field.type("00FF00")

    submit_button = owner_page.locator("button[type='submit']", has_text="Submit")
    submit_button.click()

    reamining_enums = CustomAttributeEnum.objects.filter(attribute=attribute.id)
    assert reamining_enums.count() == 1
    custom_enum = reamining_enums.first()
    assert custom_enum
    assert str(custom_enum.label) == "Low Priority"
    assert str(custom_enum.value) == "low"
    assert str(custom_enum.color_code) == "00FF00"
