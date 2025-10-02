# mypy: disable-error-code="list-item, return-value"

from textwrap import dedent
from typing import cast

import pytest
from django.template import TemplateDoesNotExist

from sandwich.core.factories import TemplateFactory
from sandwich.core.models import Organization
from sandwich.core.models import Template
from sandwich.core.service.template_service import render_template


@pytest.fixture
def common_templates(db) -> dict[str, Template]:
    templates = [
        cast(
            "Template",
            TemplateFactory(
                organization=None,
                slug="template/base",
                content=dedent("""
                    1: {% include "template/one" %}
                    2: {% include "template/two" %}
                    """),
            ),
        ),
        cast(
            "Template",
            TemplateFactory(organization=None, slug="template/one", content="Common One"),
        ),
        cast(
            "Template",
            TemplateFactory(organization=None, slug="template/two", content="Common Two"),
        ),
    ]
    return {t.slug: t for t in templates}


def clone_templates(
    templates: dict[str, Template], organization: Organization | None, name: str, old_name: str = "Common"
) -> dict[str, Template]:
    result = {}
    for template in templates.values():
        result[template.slug] = TemplateFactory(
            organization=organization, slug=template.slug, content=template.content.replace(old_name, name)
        )
    return result


@pytest.fixture
def organization_templates(
    db, organization: Organization, common_templates: dict[str, Template]
) -> dict[str, Template]:
    return clone_templates(common_templates, organization, "Org")


@pytest.fixture
def other_organization_templates(
    db, other_organization: Organization, common_templates: dict[str, Template]
) -> dict[str, Template]:
    return clone_templates(common_templates, other_organization, "Other")


@pytest.fixture
def partial_common_templates(db, common_templates: dict[str, Template]) -> dict[str, Template]:
    common_templates.pop("template/one").delete()
    return common_templates


@pytest.fixture
def partial_organization_templates(db, organization_templates: dict[str, Template]) -> dict[str, Template]:
    organization_templates.pop("template/one").delete()
    return organization_templates


def test_common(common_templates: dict[str, Template]) -> None:
    assert render_template(common_templates["template/base"]) == "<p>1: Common One\n2: Common Two</p>\n"


def test_organization(organization_templates: dict[str, Template]) -> None:
    assert render_template(organization_templates["template/base"]) == "<p>1: Org One\n2: Org Two</p>\n"


def test_organization_overrides(
    db, partial_organization_templates: dict[str, Template], common_templates: dict[str, Template]
) -> None:
    assert render_template(partial_organization_templates["template/base"]) == "<p>1: Common One\n2: Org Two</p>\n"


def test_other_organization_overrides(
    db,
    other_organization_templates: dict[str, Template],
    partial_organization_templates: dict[str, Template],
    partial_common_templates: dict[str, Template],
) -> None:
    with pytest.raises(TemplateDoesNotExist):
        render_template(partial_organization_templates["template/base"])
