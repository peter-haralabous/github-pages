import pytest
from django.test import Client
from django.urls import reverse
from playwright.sync_api import Page
from pytest_django.live_server_helper import LiveServer

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Fact
from sandwich.core.models.patient import Patient
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_details(user: User, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    res = client.get(
        reverse(
            "patients:patient_details",
            kwargs={
                "patient_id": patient.id,
            },
        )
    )

    assert res.status_code == 200


@pytest.mark.django_db
# NB: patient fixture required
def test_patient_details_deny_access(user: User, patient: Patient) -> None:
    other_patient = PatientFactory.create()
    client = Client()
    client.force_login(user)
    res = client.get(
        reverse(
            "patients:patient_details",
            kwargs={
                "patient_id": other_patient.id,
            },
        )
    )

    assert res.status_code == 404


def test_patient_details_kg(
    db, client: Client, user: User, patient: Patient, patient_knowledge_graph: list[Fact]
) -> None:
    """Test that patient details page loads with chatty app (facts are loaded dynamically)."""
    client.force_login(user)
    url = reverse("patients:patient_details", kwargs={"patient_id": patient.pk})
    response = client.get(url)

    # Chatty app provides records_count and repository_count instead of facts
    assert "records_count" in response.context
    assert "repository_count" in response.context
    assert response.status_code == 200


def login(live_server: LiveServer, page: Page, user: User) -> Page:
    page.goto(f"{live_server.url}{reverse('account_login')}")
    page.get_by_role("textbox", name="Email*").click()
    page.get_by_role("textbox", name="Email*").fill(user.email)
    page.get_by_role("textbox", name="Password*").click()
    page.get_by_role("textbox", name="Password*").fill(user.raw_password)  # type: ignore[attr-defined]
    page.get_by_role("checkbox", name="Remember Me").check()
    page.get_by_role("button", name="Sign In").click()
    return page


@pytest.fixture
def patient_page(live_server: LiveServer, page: Page, patient: Patient) -> Page:
    return login(live_server, page, patient.user)  # type: ignore[arg-type]
