from typing import Any

import pytest
from django.db import IntegrityError

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.factories.summary_template import SummaryTemplateFactory
from sandwich.core.models import Organization
from sandwich.core.models import SummaryTemplate


def test_create_summary_template(db: Any, organization: Organization) -> None:
    form = FormFactory.create(organization=organization, name="Visit Note Form")
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Visit Note",
        description="Standard visit note template",
        text="# Visit Note\n\n{% ai 'Chief Complaint' %}...",
    )

    assert template.id is not None
    assert template.name == "Visit Note"
    assert template.description == "Standard visit note template"
    assert str(template) == f"Visit Note ({organization.slug})"


def test_unique_name_per_organization(db: Any, organization: Organization) -> None:
    form = FormFactory.create(organization=organization, name="Test Form")
    SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Visit Note",
        text="Template 1",
    )

    with pytest.raises(IntegrityError):
        SummaryTemplateFactory.create(
            organization=organization,
            form=form,
            name="Visit Note",  # Duplicate name in same org
            text="Template 2",
        )


def test_same_name_different_organizations(db: Any, organization: Organization) -> None:
    org2 = OrganizationFactory.create()

    form1 = FormFactory.create(organization=organization, name="Form 1")
    form2 = FormFactory.create(organization=org2, name="Form 2")

    template1 = SummaryTemplateFactory.create(
        organization=organization,
        form=form1,
        name="Visit Note",
        text="Template 1",
    )

    template2 = SummaryTemplateFactory.create(
        organization=org2,
        form=form2,
        name="Visit Note",  # Same name, different org - OK
        text="Template 2",
    )

    assert template1.id != template2.id


def test_associate_with_form(db: Any, organization: Organization) -> None:
    form = FormFactory.create(organization=organization, name="Intake Form")

    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Intake Summary",
        text="...",
    )

    assert template.form == form
    assert template in form.summarytemplate_set.all()


def test_template_without_description(db: Any, organization: Organization) -> None:
    form = FormFactory.create(organization=organization, name="Simple Form")
    template = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Simple Template",
        text="# Simple",
    )

    assert template.description == ""


def test_template_ordering(db: Any, organization: Organization) -> None:
    form = FormFactory.create(organization=organization, name="Test Form")
    template_z = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Zebra Template",
        text="...",
    )
    template_a = SummaryTemplateFactory.create(
        organization=organization,
        form=form,
        name="Alpha Template",
        text="...",
    )

    templates = list(SummaryTemplate.objects.filter(organization=organization))

    assert templates[0] == template_a
    assert templates[1] == template_z
