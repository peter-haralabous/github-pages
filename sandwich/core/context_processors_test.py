from sandwich.core.context_processors import patients_context
from sandwich.core.context_processors import settings_context
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.util.testing import UserRequestFactory
from sandwich.users.models import User


def test_settings_context(user: User, urf: UserRequestFactory):
    request = urf.get("/")
    context = settings_context(request)
    assert "datadog_vars" in context
    assert "environment" in context["datadog_vars"]
    assert "app_version" in context["datadog_vars"]
    assert context["datadog_vars"]["user_id"] is None

    user_request = urf(user).get("/")
    context = settings_context(user_request)
    assert context["datadog_vars"]["user_id"] == user.id


def test_patients_context_anonymous(urf: UserRequestFactory):
    request = urf.get("/")
    context = patients_context(request)
    assert context == {}


def test_patients_context_authenticated(user: User, urf: UserRequestFactory):
    patient1 = PatientFactory(user=user)
    patient2 = PatientFactory(user=user)
    request = urf(user).get("/")
    context = patients_context(request)

    assert "user_patients" in context
    assert len(context["user_patients"]) == 2
    assert patient1 in context["user_patients"]
    assert patient2 in context["user_patients"]


def test_patients_context_authenticated_no_patients(user: User, urf: UserRequestFactory):
    request = urf(user).get("/")
    context = patients_context(request)

    assert "user_patients" in context
    assert len(context["user_patients"]) == 0
