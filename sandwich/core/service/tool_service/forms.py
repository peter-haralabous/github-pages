import logging
import uuid
from copy import deepcopy
from typing import Any

from django.db import transaction
from langchain_core.tools import BaseTool
from langchain_core.tools import tool
from pydantic import BaseModel

from sandwich.core.models.form import Form

logger = logging.getLogger(__name__)

# Note(MM): Instead of writing to the db directly from tools, a possible
# improvement here would be to use graph state to track a working copy of the
# form schema that tools can make changes to. Once the agent has completed its
# tool calls, we pull the schema of out of state and write it to the database.
#
# We cut down on db calls, but lose granularity in form "edit" history.


class NewPageArgs(BaseModel):
    page_name: str
    page_title: str
    elements: list[dict[str, Any]] | None = None


class AppendToPageArgs(BaseModel):
    page_name: str
    elements: list[dict[str, Any]] | None = None


def build_add_new_page_to_schema_tool(target_form_id: uuid.UUID) -> BaseTool:
    @tool(
        "add_new_page_to_schema",
        description="Adds a new page to the SurveyJS form schema.",
        args_schema=NewPageArgs,
    )
    def add_new_page_to_schema(page_name: str, page_title: str, elements: list[dict[str, Any]] | None = None) -> None:
        with transaction.atomic():
            # NB: Despite asking the LLM to run tools synchronously, put a
            # lock on the object we're updating as an extra layer of safety.
            form = Form.objects.select_for_update().get(id=target_form_id)

            new_page = {"name": page_name, "title": page_title, "elements": elements if elements else []}
            logger.info(
                "add_new_page_to_schema tool generating page",
                extra={"page_name": page_name, "page_title": page_title},
            )
            form.schema.setdefault("pages", []).append(new_page)
            form.full_clean()
            form.save()

    return add_new_page_to_schema


def build_append_elements_to_existing_page_tool(target_form_id: uuid.UUID) -> BaseTool:
    @tool(
        "append_elements_to_existing_page",
        description="Append elements to an existing page in the form schema.",
        args_schema=AppendToPageArgs,
    )
    def append_elements_to_existing_page(page_name: str, elements: list[dict[str, Any]]) -> None:
        # NB: Despite asking the LLM to run tools synchronously, put a
        # lock on the object we're updating as an extra layer of safety.
        with transaction.atomic():
            target_page: dict[str, Any] | None = None
            form = Form.objects.select_for_update().get(id=target_form_id)
            updated_schema = deepcopy(form.schema)
            schema_pages = updated_schema.get("pages")
            if not schema_pages:
                raise ValueError("This schema has no pages.")

            for page in schema_pages:
                if page.get("name") == page_name:
                    target_page = page
                    break
            if not target_page:
                raise ValueError(f"Could not find the page {page_name}")

            logger.info(
                "append_elements_to_existing_page tool appending elements to page", extra={"page_name": page_name}
            )
            target_page.setdefault("elements", []).extend(elements)
            form.schema = updated_schema
            form.full_clean()
            form.save()

    return append_elements_to_existing_page
