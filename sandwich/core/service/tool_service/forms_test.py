import pytest

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
