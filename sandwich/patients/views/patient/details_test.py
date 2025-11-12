import pytest
from django.test import Client
from django.urls import reverse
from playwright.sync_api import Page
from playwright.sync_api import expect
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


@pytest.mark.e2e
def test_patient_display_fact(
    live_server: LiveServer,
    patient_page: Page,
    patient: Patient,
    patient_knowledge_graph: list[Fact],
):
    patient_page.goto(f"{live_server.url}{reverse('patients:patient_details', args=(patient.id,))}")

    for i, fact in enumerate(patient_knowledge_graph):
        fact_edit = patient_page.get_by_test_id(f"fact-{fact.id}-edit")
        assert fact_edit.is_visible(), f"Fact #{i} edit button should be visible"


@pytest.mark.e2e
def test_patient_edit_fact(
    live_server: LiveServer,
    patient_page: Page,
    patient: Patient,
    patient_knowledge_graph: list[Fact],
):
    patient_page.goto(f"{live_server.url}{reverse('patients:patient_details', args=(patient.id,))}")
    fact = patient_knowledge_graph[0]

    # Edit the start date of the first fact
    patient_page.get_by_test_id(f"fact-{fact.id}-edit").click()
    patient_page.get_by_role("textbox", name="Start Date/Time").fill("1990-01-01T00:00", timeout=1000)
    patient_page.get_by_role("button", name="Save").click()
    # Display is updated
    expect(patient_page.get_by_test_id(f"fact-{fact.id}-start-datetime")).to_contain_text("1 Jan 1990")

    # Try to set the end date before the start date
    patient_page.get_by_test_id(f"fact-{fact.id}-edit").click()
    patient_page.get_by_role("textbox", name="End Date/Time").fill("1989-01-01T00:00", timeout=1000)
    patient_page.get_by_role("button", name="Save").click()
    # Error displayed
    expect(patient_page.get_by_text("cannot be earlier")).to_be_visible()

    # Try to set the end date in the future
    patient_page.get_by_role("textbox", name="End Date/Time").fill("3500-01-01T00:00", timeout=1000)
    patient_page.get_by_role("button", name="Save").click()
    # Error displayed
    expect(patient_page.get_by_text("in the future")).to_be_visible()

    # Set the end date correctly
    patient_page.get_by_role("textbox", name="End Date/Time").fill("1991-01-01T00:00", timeout=1000)
    patient_page.get_by_role("button", name="Save").click()
    # Display is updated
    expect(patient_page.get_by_test_id(f"fact-{fact.id}-end-datetime")).to_contain_text("1 Jan 1991")
