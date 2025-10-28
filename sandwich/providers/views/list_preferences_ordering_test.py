"""Unit tests for preference modal column ordering logic."""

from __future__ import annotations

from sandwich.core.models import ListViewType
from sandwich.core.service.list_preference_service import get_available_columns
from sandwich.providers.views.list_preferences import build_columns_data


def test_build_columns_data_orders_visible_first():
    """Visible columns should appear first preserving saved order."""
    available = get_available_columns(ListViewType.ENCOUNTER_LIST)
    # simulate user re-ordered columns: last updated first, then status, then email
    visible = ["updated_at", "patient_status", "patient__email"]
    data = build_columns_data(available, visible)
    # First three entries correspond to visible list in same order
    assert [d["value"] for d in data[:3]] == visible
    # Remaining available but not visible columns appear afterwards in original available order
    remaining_values = [d["value"] for d in data[3:]]
    expected_remaining = [v for v in [c["value"] for c in available] if v not in set(visible)]
    assert remaining_values == expected_remaining


def test_build_columns_data_filters_obsolete():
    """Obsolete visible column values not in available columns should be ignored."""
    available = get_available_columns(ListViewType.PATIENT_LIST)
    visible = ["first_name", "NON_EXISTENT", "email"]
    data = build_columns_data(available, visible)
    # NON_EXISTENT should not appear
    values = [d["value"] for d in data]
    assert "NON_EXISTENT" not in values
    # Order keeps first_name then email at front
    assert values[0] == "first_name"
    assert values[1] == "email"


def test_build_columns_data_checked_flags():
    """Checked flag should be set only for visible columns."""
    available = get_available_columns(ListViewType.PATIENT_LIST)
    visible = ["email"]
    data = build_columns_data(available, visible)
    for entry in data:
        assert entry["checked"] is (entry["value"] in visible)


def test_build_columns_data_empty_visible():
    """When no visible columns, ordering should match available and none checked."""
    available = get_available_columns(ListViewType.PATIENT_LIST)
    visible: list[str] = []
    data = build_columns_data(available, visible)
    assert [d["value"] for d in data] == [c["value"] for c in available]
    assert all(not d["checked"] for d in data)
