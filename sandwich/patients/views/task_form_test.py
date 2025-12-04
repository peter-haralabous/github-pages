import urllib.parse

import pytest
from django.urls import reverse
from playwright.sync_api import Page
from playwright.sync_api import expect

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import TaskStatus


@pytest.mark.e2e
def test_task_form_component_renders(live_server, page: Page, patient: Patient, auth_cookies: None):
    """Validate patient task form load and assert the SurveyForm renders properly."""
    schema = {"elements": [{"type": "text", "name": "yourName", "title": "What is your name?"}]}
    form = FormFactory.create(name="E2E Test Form", schema=schema, organization=patient.organization)
    task = TaskFactory.create(patient=patient, form_version=form.events.last())

    task_url_path = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    url = f"{live_server.url}{task_url_path}"

    # Navigate to the task page and wait for the important selectors below.
    page.goto(url)
    page.wait_for_selector("survey-form", state="attached", timeout=5000)

    script_sel = "#form_schema[type='application/json']"
    page.wait_for_selector(script_sel, state="attached", timeout=5000)
    script_el = page.query_selector(script_sel)
    assert script_el is not None
    text = script_el.text_content()
    assert "yourName" in (text or "")

    page.wait_for_selector("survey-form [data-survey-container][data-survey-rendered]", timeout=5000)

    input_by_label = page.get_by_label("What is your name?")
    assert input_by_label is not None
    # ensure the element exists and is visible
    assert input_by_label.count() > 0, "Expected an input labelled 'What is your name?' to be present"
    assert input_by_label.first.is_visible(), "Expected the 'yourName' input to be visible"


@pytest.mark.e2e
def test_task_form_submit_shows_success(live_server, page: Page, patient: Patient, auth_cookies: None):
    """Submit a small form and assert the POST happens and the UI shows success."""
    schema = {"elements": [{"type": "text", "name": "yourName", "title": "What is your name?"}]}
    form = FormFactory.create(name="E2E Submit Form", schema=schema, organization=patient.organization)
    task = TaskFactory.create(patient=patient, form_version=form.events.last())

    task_url_path = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    url = f"{live_server.url}{task_url_path}"

    page.goto(url)
    page.wait_for_selector("survey-form", state="attached", timeout=5000)

    # obtain the submit URL from the component attributes so we can watch for that request
    submit_url = page.eval_on_selector("survey-form", "el => el.getAttribute('data-submit-url')")
    assert submit_url, "submit URL should be present on the survey-form element"

    # Normalize to a full URL and extract path for robust request matching
    full_submit_url = f"{live_server.url.rstrip('/')}{submit_url}" if submit_url.startswith("/") else submit_url
    submit_path = urllib.parse.urlparse(full_submit_url).path

    # wait for schema script and survey to render
    page.wait_for_selector("#form_schema[type='application/json']", state="attached", timeout=5000)
    page.wait_for_selector("survey-form [data-survey-container][data-survey-rendered]", timeout=5000)

    # fill the required input
    name_input = page.get_by_label("What is your name?")
    assert name_input.count() > 0
    name_input.first.fill("Alice")

    complete_timeout = 15000
    with page.expect_request(
        lambda r: r.method == "POST" and urllib.parse.urlparse(r.url).path == submit_path,
        timeout=complete_timeout,
    ) as req_info:
        complete_button = page.get_by_role("button", name="Complete")
        complete_button.click()

    success_selector = "text=Form successfully submitted"
    page.wait_for_selector(success_selector, timeout=5000)

    request = req_info.value
    assert request is not None
    body = request.post_data
    assert body is not None
    assert "yourName" in (body or ""), "Submission payload should contain the question name"


@pytest.mark.e2e
def test_task_form_component_renders_read_only(live_server, page: Page, patient: Patient, auth_cookies: None):
    schema = {"elements": [{"type": "text", "name": "yourName", "title": "What is your name?"}]}
    form = FormFactory.create(name="E2E Test Form", schema=schema, organization=patient.organization)
    task = TaskFactory.create(patient=patient, form_version=form.events.last(), status=TaskStatus.COMPLETED)

    task_url_path = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    url = f"{live_server.url}{task_url_path}"
    page.goto(url)

    page.wait_for_selector("survey-form [data-survey-container][data-survey-rendered]", timeout=5000)

    name_input = page.get_by_label("What is your name?")
    assert name_input is not None
    expect(name_input).to_have_attribute("readonly", "")
