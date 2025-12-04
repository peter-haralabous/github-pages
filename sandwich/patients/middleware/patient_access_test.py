import pytest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

from sandwich.core.util.testing import UserRequestFactory
from sandwich.patients.middleware.patient_access import PatientAccessMiddleware
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_access_middleware(user: User, urf: UserRequestFactory):
    """
    GIVEN a user without a patient
    WHEN they try to access a page that is not on the allowed list
    THEN they should be redirected to the add patient page
    """
    request = urf(user).get(reverse("patients:home"))
    middleware = PatientAccessMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("patients:patient_onboarding_add")


@pytest.mark.django_db
def test_patient_access_middleware_allowed_route(user: User, urf: UserRequestFactory):
    """
    GIVEN a user without a patient
    WHEN they try to access a page that is on the allowed list
    THEN they should be allowed to access the page
    """
    request = urf(user).get(reverse("patients:patient_onboarding_add"))
    middleware = PatientAccessMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)
    assert response.status_code == 200
