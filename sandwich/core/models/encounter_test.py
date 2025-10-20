from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus


def test_encounter_search(db) -> None:
    organization = OrganizationFactory.create()

    # this patient should match
    patient = PatientFactory.create(organization=organization, first_name="Vannevar", last_name="Bush")
    encounter = Encounter.objects.create(
        patient=patient, organization=organization, status=EncounterStatus.IN_PROGRESS
    )

    # another one that should not match
    Encounter.objects.create(
        patient=PatientFactory.create(organization=organization, first_name="Jimbo", last_name="Wales"),
        organization=organization,
        status=EncounterStatus.IN_PROGRESS,
    )

    assert list(Encounter.objects.search("Vannevar Bush")) == [encounter]
