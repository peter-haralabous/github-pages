# mypy: disable-error-code="list-item, return-value"

from collections.abc import Collection
from textwrap import dedent
from typing import cast

import pytest
from django.template.exceptions import TemplateDoesNotExist

from sandwich.core.factories import TemplateFactory
from sandwich.core.models import Organization
from sandwich.core.models import Template
from sandwich.core.service.template_service import LoaderDefinitions
from sandwich.core.service.template_service import render
from sandwich.core.service.template_service import render_template

template_content = {  # double braces because of .format usage
    "base": dedent("""
        1: {{% include "one" %}}
        2: {{% include "two" %}}
        """),
    "one": "{name} One",
    "two": "{name} Two",
}


def build_templates(
    organization: Organization | None, name: str, exclude: Collection[str] | None = None
) -> dict[str, Template]:
    exclude = exclude or set()
    return {
        slug: cast(
            "Template", TemplateFactory(organization=organization, slug=slug, content=content.format(name=name))
        )
        for slug, content in template_content.items()
        if slug not in exclude
    }


@pytest.fixture
def common_templates(db, organization: Organization) -> dict[str, Template]:
    return build_templates(None, "Common")


@pytest.fixture
def organization_templates(db, organization: Organization) -> dict[str, Template]:
    return build_templates(organization, "Org")


@pytest.fixture
def other_organization_templates(db, other_organization: Organization) -> dict[str, Template]:
    return build_templates(other_organization, "Other")


@pytest.fixture
def partial_common_templates(db) -> dict[str, Template]:
    return build_templates(None, "Common", exclude={"one"})


@pytest.fixture
def partial_organization_templates(db, organization: Organization) -> dict[str, Template]:
    return build_templates(organization, "Org", exclude={"one"})


def test_render_template_common(common_templates: dict[str, Template]) -> None:
    assert render_template(common_templates["base"]) == "<p>1: Common One\n2: Common Two</p>\n"


def test_render_template_organization(organization_templates: dict[str, Template]) -> None:
    assert render_template(organization_templates["base"]) == "<p>1: Org One\n2: Org Two</p>\n"


def test_render_template_organization_overrides(
    db, partial_organization_templates: dict[str, Template], common_templates: dict[str, Template]
) -> None:
    assert render_template(partial_organization_templates["base"]) == "<p>1: Common One\n2: Org Two</p>\n"


def test_render_template_other_organization_overrides(
    db,
    other_organization_templates: dict[str, Template],
    partial_organization_templates: dict[str, Template],
    partial_common_templates: dict[str, Template],
) -> None:
    with pytest.raises(TemplateDoesNotExist):
        render_template(partial_organization_templates["base"])


@pytest.fixture
def loaders() -> LoaderDefinitions:
    return [
        (
            "django.template.loaders.locmem.Loader",
            {
                "one": "Memory One",
                "two": "Memory Two",
            },
        )
    ]


def test_render_multiple_loader(loaders: LoaderDefinitions, partial_common_templates: dict[str, Template]) -> None:
    assert (
        render(
            "base",
            loaders=loaders,
        )
        == "<p>1: Memory One\n2: Common Two</p>\n"
    )
