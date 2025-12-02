import pytest
from django.core.exceptions import ValidationError

from sandwich.core.factories.form import FormFactory
from sandwich.core.service.tool_service.forms import build_add_new_page_to_schema_tool
from sandwich.core.service.tool_service.forms import build_append_elements_to_existing_page_tool


@pytest.mark.django_db(transaction=True)
def test_append_elements_to_existing_page() -> None:
    form = FormFactory.create(
        schema={"title": "Test form", "pages": [{"name": "page1", "elements": [{"name": "f_name", "type": "text"}]}]}
    )

    tool = build_append_elements_to_existing_page_tool(form.id)
    tool.run(
        {"page_name": "page1", "elements": [{"name": "l_name", "type": "text"}, {"name": "age", "type": "number"}]}
    )

    form.refresh_from_db()
    assert len(form.schema["pages"][0]["elements"]) == 3
    assert form.schema["pages"][0]["elements"][1]["name"] == "l_name"
    assert form.schema["pages"][0]["elements"][2]["name"] == "age"


@pytest.mark.django_db(transaction=True)
def test_add_new_page_to_schema() -> None:
    form = FormFactory.create(
        schema={
            "title": "Test form",
            "pages": [
                {
                    "name": "page1",
                }
            ],
        }
    )

    tool = build_add_new_page_to_schema_tool(form.id)
    tool.run(
        {
            "page_name": "page2",
            "page_title": "Second Page",
            "elements": [{"name": "l_name", "type": "text"}, {"name": "age", "type": "number"}],
        }
    )

    form.refresh_from_db()
    assert len(form.schema["pages"]) == 2
    assert form.schema["pages"][1]["name"] == "page2"


@pytest.mark.django_db(transaction=True)
def test_add_new_page_returns_error_string_on_invalid_schema() -> None:
    """
    Verifies that the tool catches validation errors and returns them as a string.
    """
    form = FormFactory.create(schema={})
    tool = build_add_new_page_to_schema_tool(form.id)

    invalid_args = {
        "page_name": "page1",
        "page_title": "Page 1",
        "elements": [
            {
                "type": "text",
                "name": "q1",
                "readOnly": "true",  # INVALID
            }
        ],
    }
    with pytest.raises(ValidationError) as e:
        tool.run(invalid_args)

    error_msg = str(e.value)
    assert "is not valid under any of the given schemas" in error_msg

    form.refresh_from_db()
    assert form.schema == {}


@pytest.mark.django_db(transaction=True)
def test_agent_retry_simulation_workflow() -> None:
    """
    This test mimics the loop behavior.
    Retries with valid data.
    """
    form = FormFactory.create(schema={})
    tool = build_add_new_page_to_schema_tool(form.id)

    bad_input = {
        "page_name": "p1",
        "page_title": "T",
        "elements": [{"type": "text", "name": "q1", "visible": "false"}],
    }
    with pytest.raises(ValidationError):
        tool.run(bad_input)

    form.refresh_from_db()
    assert form.schema == {}

    # The Agent fixes the input based on the error
    good_input = {
        "page_name": "p1",
        "page_title": "T",
        "elements": [{"type": "text", "name": "q1", "visible": False}],
    }

    tool.run(good_input)

    # The DB is updated
    form.refresh_from_db()
    assert form.schema["pages"][0]["elements"][0]["visible"] is False


@pytest.mark.django_db(transaction=True)
def test_append_elements_returns_error_string_on_invalid_schema() -> None:
    """
    Verifies that appending invalid elements is caught by validation
    """
    initial_schema = {"pages": [{"name": "target_page", "elements": [{"type": "text", "name": "existing_q"}]}]}
    form = FormFactory.create(schema=initial_schema)
    tool = build_append_elements_to_existing_page_tool(form.id)

    invalid_args = {
        "page_name": "target_page",
        "elements": [
            {
                "type": "text",
                "name": "new_q",
                "isRequired": "yes",  # INVALID
            }
        ],
    }
    with pytest.raises(ValidationError):
        tool.run(invalid_args)

    form.refresh_from_db()
    page_elements = form.schema["pages"][0]["elements"]

    assert len(page_elements) == 1
    assert page_elements[0]["name"] == "existing_q"


@pytest.mark.django_db(transaction=True)
def test_append_elements_retry_simulation_workflow() -> None:
    """
    Simulates the Agent workflow by appending invalid then valid data
    """
    initial_schema = {"pages": [{"name": "target_page", "elements": []}]}
    form = FormFactory.create(schema=initial_schema)
    tool = build_append_elements_to_existing_page_tool(form.id)

    bad_input = {"page_name": "target_page", "elements": [{"type": "text", "name": "q1", "isRequired": "true"}]}
    with pytest.raises(ValidationError):
        tool.run(bad_input)

    form.refresh_from_db()
    assert len(form.schema["pages"][0]["elements"]) == 0

    good_input = {"page_name": "target_page", "elements": [{"type": "text", "name": "q1", "isRequired": True}]}
    tool.run(good_input)

    form.refresh_from_db()
    new_element = form.schema["pages"][0]["elements"][0]
    assert new_element["name"] == "q1"
    assert new_element["isRequired"] is True
