from sandwich.core.service.prompt_service.chat import patient_context
from sandwich.core.service.prompt_service.chat import user_context


def test_patient_context(patient):
    context = patient_context(patient)
    assert patient.full_name in context


def test_user_context(user):
    context = user_context(user)
    assert user.get_full_name() in context
