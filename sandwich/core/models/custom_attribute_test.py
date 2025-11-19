import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
from sandwich.core.models.custom_attribute import CustomAttributeValue
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus


@pytest.fixture
def date_attribute(organization):
    return CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Test Date Attribute",
        data_type=CustomAttribute.DataType.DATE,
    )


@pytest.fixture
def enum_attribute(organization):
    return CustomAttribute.objects.create(
        organization=organization,
        content_type=ContentType.objects.get_for_model(Encounter),
        name="Test Enum Attribute",
        data_type=CustomAttribute.DataType.ENUM,
    )


@pytest.fixture
def enum_values(enum_attribute):
    low = CustomAttributeEnum.objects.create(attribute=enum_attribute, label="Low", value="low")
    high = CustomAttributeEnum.objects.create(attribute=enum_attribute, label="High", value="high")
    return {"low": low, "high": high}


@pytest.mark.django_db
def test_custom_date_attribute(encounter, date_attribute) -> None:
    # add a value for the custom attribute to the encounter
    encounter.attributes.create(attribute=date_attribute, value_date="2024-01-01")

    # read back and verify
    value = encounter.attributes.get(attribute=date_attribute)
    assert value.value_date.isoformat() == "2024-01-01"


@pytest.mark.django_db
def test_custom_enum_attribute(encounter, enum_attribute, enum_values) -> None:
    # add a value for the custom attribute to the encounter
    encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["high"])

    # read back and verify
    value = encounter.attributes.get(attribute=enum_attribute)
    assert value.value_enum == enum_values["high"]


@pytest.mark.django_db
def test_custom_attribute_filtering(patient, organization, enum_attribute, enum_values) -> None:
    encounter1 = Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.UNKNOWN)
    encounter2 = Encounter.objects.create(patient=patient, organization=organization, status=EncounterStatus.UNKNOWN)

    # add values for the custom attribute to the encounters
    encounter1.attributes.create(attribute=enum_attribute, value_enum=enum_values["high"])
    encounter2.attributes.create(attribute=enum_attribute, value_enum=enum_values["low"])

    # filter encounters by custom attribute value
    # TODO: this is too verbose; consider adding a helper method on the manager
    high_priority_encounters = Encounter.objects.filter(
        attributes__attribute=enum_attribute, attributes__value_enum=enum_values["high"]
    )

    assert high_priority_encounters.count() == 1
    assert high_priority_encounters.first() == encounter1


@pytest.mark.django_db
def test_custom_attribute_organization_isolation(enum_attribute, enum_values):
    other_org = OrganizationFactory.create()
    other_patient = PatientFactory.create(organization=other_org, first_name="Other", last_name="Patient")
    other_encounter = Encounter.objects.create(
        patient=other_patient, organization=other_org, status=EncounterStatus.UNKNOWN
    )

    with pytest.raises(ValidationError, match="Attribute organization must match content object's organization"):
        other_encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["low"]).clean()


# - ensure that an attribute defined for one model cannot be used in another model
@pytest.mark.django_db
def test_custom_attribute_content_type_isolation(enum_attribute, enum_values):
    patient = PatientFactory.create(
        organization=enum_attribute.organization, first_name="Isolated", last_name="Patient"
    )
    with pytest.raises(ValidationError, match="Attribute content_type must match the content_type of the value"):
        CustomAttributeValue.objects.create(
            content_object=patient, attribute=enum_attribute, value_enum=enum_values["low"]
        ).clean()


# - ensure that data_type and value_x fields align
@pytest.mark.django_db
def test_custom_attribute_data_type_enforcement(encounter, date_attribute, enum_attribute, enum_values):
    # Attempt to add an ENUM value to a DATE attribute
    with pytest.raises(ValidationError, match=r"value_date must be set for date attributes"):
        encounter.attributes.create(attribute=date_attribute, value_enum=enum_values["low"])

    # Attempt to add a DATE value to an ENUM attribute
    with pytest.raises(ValidationError, match=r"value_enum must be set for enum attributes"):
        encounter.attributes.create(attribute=enum_attribute, value_date="2024-01-01")


# - ensure that multiple value for the same attribute can be added *if* is_multi is True
@pytest.mark.django_db
def test_custom_attribute_multi_value_violation(encounter, enum_attribute, enum_values):
    # Add multiple values
    encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["low"])
    with pytest.raises(ValidationError, match="Attribute cannot have multiple values for this object"):
        encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["high"]).clean()


@pytest.mark.django_db
def test_custom_attribute_multi_value(encounter, enum_attribute, enum_values):
    # Set the attribute to be multi-valued
    enum_attribute.is_multi = True
    enum_attribute.save()

    # Add multiple values
    encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["low"])
    encounter.attributes.create(attribute=enum_attribute, value_enum=enum_values["high"])

    # Verify both values exist
    values = encounter.attributes.filter(attribute=enum_attribute)
    assert values.count() == 2
    assert {v.value_enum for v in values} == {enum_values["low"], enum_values["high"]}
