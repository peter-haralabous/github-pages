from sandwich.core.factories.consent import ConsentFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models import Consent
from sandwich.core.models import Encounter
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models.consent import ConsentPolicy
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.task import Task
from sandwich.users.factories import UserFactory
from sandwich.users.models import User


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.pk}/"


def test_users_delete_account(user: User, organization: Organization) -> None:
    """Account deletion should cascade to related objects like patients, encounters, tasks, etc."""
    # Associate patients, tasks, etc for deletion.
    ConsentFactory.create(user=user, policy=ConsentPolicy.THRIVE_TERMS_OF_USE, decision=True)
    my_patient = PatientFactory.create(user=user, first_name="Me", organization=organization)
    my_child_patient = PatientFactory.create(user=user, first_name="My kid", organization=organization)
    my_encounter = Encounter.objects.create(
        patient=my_patient, organization=organization, status=EncounterStatus.IN_PROGRESS
    )
    my_childs_encounter = Encounter.objects.create(
        patient=my_child_patient, organization=organization, status=EncounterStatus.IN_PROGRESS
    )
    my_task = TaskFactory.create(patient=my_patient, encounter=my_encounter)
    my_childs_task = TaskFactory.create(patient=my_child_patient, encounter=my_childs_encounter)

    my_id = user.id
    user.delete_account()

    # Confirm all related objects are deleted
    assert User.objects.filter(pk=my_id).exists() is False
    assert Patient.objects.filter(pk=my_patient.pk).exists() is False
    assert Patient.objects.filter(pk=my_child_patient.pk).exists() is False
    assert Encounter.objects.filter(pk=my_encounter.pk).exists() is False
    assert Encounter.objects.filter(pk=my_childs_encounter.pk).exists() is False
    assert Task.objects.filter(pk=my_task.pk).exists() is False
    assert Task.objects.filter(pk=my_childs_task.pk).exists() is False
    assert Consent.objects.filter(user_id=my_id).exists() is False


def test_users_delete_account_doesnt_delete_another_users_data(user: User, organization: Organization) -> None:
    """
    Account deletion should not cascade to other users' related objects.
    """
    my_patient = PatientFactory.create(user=user, first_name="Me", organization=organization)

    your_user = UserFactory.create(name="You")
    your_patient = PatientFactory.create(user=your_user, first_name="You", organization=organization)
    your_encounter = Encounter.objects.create(
        patient=your_patient, organization=organization, status=EncounterStatus.IN_PROGRESS
    )
    your_task = TaskFactory.create(patient=your_patient, encounter=your_encounter)

    my_id = user.id
    user.delete_account()

    # I am deleted
    assert User.objects.filter(pk=my_id).exists() is False
    assert Patient.objects.filter(pk=my_patient.pk).exists() is False
    # You are not
    assert User.objects.filter(pk=your_user.id).exists() is True
    assert Patient.objects.filter(pk=your_patient.pk).exists() is True
    assert Encounter.objects.filter(pk=your_encounter.pk).exists() is True
    assert Task.objects.filter(pk=your_task.pk).exists() is True
