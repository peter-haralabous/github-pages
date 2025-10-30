from typing import Any

import pytest
from django.db import IntegrityError

from sandwich.core.models import Organization
from sandwich.core.models.form import Form


def test_form_create(db: Any, organization: Organization) -> None:
    form = Form.objects.create(name="Test Form", schema={"foo": "bar"}, organization=organization)
    assert form.pk is not None
    assert form.name == "Test Form"
    assert form.schema == {"foo": "bar"}
    assert form.organization == organization
    with pytest.raises(IntegrityError):
        # Duplicate form name in same org raises error.
        Form.objects.create(name="Test Form", schema={"baz": "zooka"}, organization=organization)


def test_form_versions(db: Any, organization: Organization) -> None:
    """Show that the Form model's versioning works as expected."""
    # Create form 1, version 1.
    form = Form.objects.create(name="Versioned Form", schema={"initial": True}, organization=organization)

    # Confirm that an event (i.e. version) was created.
    assert form.events.count() == 1
    first_version = form.events.first()
    assert first_version is not None
    assert first_version.id == form.pk
    assert first_version.name == "Versioned Form"
    assert first_version.schema == {"initial": True}
    assert first_version.organization_id == organization.pk
    assert first_version.pgh_label == "insert"  # These can be customized
    assert form.get_total_versions() == 1  # v1

    # Update form1 and check that a new event (i.e. version) is created.
    form.name = "Updated Versioned Form"
    form.schema = {"foo": "bar"}
    form.save()
    assert form.events.count() == 2
    latest_version = form.events.last()
    assert latest_version.name == "Updated Versioned Form"
    assert latest_version.schema == {"foo": "bar"}
    assert latest_version.pgh_label == "update"
    assert form.get_total_versions() == 2  # v2

    form2 = Form.objects.create(name="Another Form", schema={"another": True}, organization=organization)

    # Shouldn't pick up a different form's events
    assert form.events.count() == 2
    assert form2.events.count() == 1


def test_mixin_get_current_version(db: Any, organization: Organization) -> None:
    """VersionMixin.get_current_version() retrieves the latest version of the model."""
    form = Form.objects.create(name="Survey", schema={"q1": "yes/no"}, organization=organization)
    form.name = "Customer Survey"
    form.save()
    form.schema = {"q1": "yes/no", "q2": "text"}
    form.save()

    current_version = form.get_current_version()
    assert current_version.name == "Customer Survey"
    assert current_version.schema == {"q1": "yes/no", "q2": "text"}


def test_mixin_get_version(db: Any, organization: Organization) -> None:
    """VersionMixin.get_version() retrieves the expected historical version of the model."""
    # Version 1.
    name_v1 = "Intake"
    schema_v1 = {"title": "Intake Screener"}
    form = Form.objects.create(name=name_v1, schema=schema_v1, organization=organization)
    v1_id = form.events.last().pgh_id
    # Version 2: change name.
    name_v2 = "Intake Form"
    schema_v2 = form.schema
    form.name = name_v2
    form.save()
    v2_id = form.events.last().pgh_id
    # Version 3: change schema.
    name_v3 = form.name
    schema_v3 = {"title": "Intake Screening Form"}
    form.schema = schema_v3
    form.save()
    v3_id = form.events.last().pgh_id

    # Get specific version of form.
    form_v1 = form.get_version(v1_id)
    assert form_v1.name == name_v1
    assert form_v1.schema == schema_v1
    assert form_v1.id == form.id

    form_v2 = form.get_version(v2_id)
    assert form_v2.name == name_v2
    assert form_v2.schema == schema_v2
    assert form_v2.id == form.id

    form_v3 = form.get_version(v3_id)
    assert form_v3.name == name_v3
    assert form_v3.schema == schema_v3
    assert form_v3.id == form.id


def test_mixin_get_past_versions(db: Any, organization: Organization) -> None:
    """VersionMixin.get_past_versions() retrieves all but the current version."""
    form = Form.objects.create(name="Registration", schema={"step1": True}, organization=organization)
    form.name = "User Registration"
    form.save()
    form.schema = {"step1": True, "step2": True}
    form.save()

    past_versions = form.get_past_versions()
    assert past_versions.count() == 2
    # current version is not in the returned list.
    assert form.events.last().pgh_id not in [v.pgh_id for v in past_versions]

    # list is returned in descending order (newest first).
    second_version = past_versions[0]
    assert second_version.name == "User Registration"
    assert second_version.schema == {"step1": True}

    first_version = past_versions[1]
    assert first_version.name == "Registration"
    assert first_version.schema == {"step1": True}


def test_mixin_get_versions(db: Any, organization: Organization) -> None:
    """VersionMixin.get_versions() retrieves all versions, including the current version."""
    form = Form.objects.create(name="Registration", schema={"step1": True}, organization=organization)
    form.name = "User Registration"
    form.save()
    form.schema = {"step1": True, "step2": True}
    form.save()

    past_versions = form.get_versions()
    assert past_versions.count() == 3

    # list is returned in descending order (newest first).
    third_version = past_versions[0]
    assert third_version.name == "User Registration"
    assert third_version.schema == {"step1": True, "step2": True}

    second_version = past_versions[1]
    assert second_version.name == "User Registration"
    assert second_version.schema == {"step1": True}

    first_version = past_versions[2]
    assert first_version.name == "Registration"
    assert first_version.schema == {"step1": True}


def test_mixin_get_total_versions(db: Any, organization: Organization) -> None:
    """VersionMixin.get_total_versions() returns the correct count of versions."""
    form = Form.objects.create(name="Feedback", schema={"feedback": ""}, organization=organization)
    assert form.get_total_versions() == 1
    form.name = "Customer Feedback"
    form.save()
    assert form.get_total_versions() == 2
    form.schema = {"feedback": "", "rating": 0}
    form.save()
    assert form.get_total_versions() == 3


def test_mixin_restore_to(db: Any, organization: Organization) -> None:
    """VersionMixin.restore_to() reverts the model to the specified version."""
    form = Form.objects.create(name="Survey", schema={"q1": "yes/no"}, organization=organization)
    v1_id = form.events.last().pgh_id
    form.name = "Customer Survey"
    form.save()
    v2_id = form.events.last().pgh_id
    form.schema = {"q1": "yes/no", "q2": "text"}
    form.save()

    assert form.events.count() == 3  # Three versions exist.

    # Current version should have the latest changes.
    assert form.name == "Customer Survey"
    assert form.schema == {"q1": "yes/no", "q2": "text"}

    # Restore to version 1.
    restored_form = form.restore_to(previous_version_id=v1_id)
    assert restored_form.name == "Survey"
    assert restored_form.schema == {"q1": "yes/no"}
    assert form.events.count() == 4  # A version was created for the restore action.

    # Restore to version 2.
    restored_form = form.restore_to(previous_version_id=v2_id)
    assert restored_form.name == "Customer Survey"
    assert restored_form.schema == {"q1": "yes/no"}
    assert form.events.count() == 5  # A version was created for the restore action.
