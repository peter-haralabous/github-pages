"""Tests for custom widgets."""

from django.http import QueryDict
from django.utils.datastructures import MultiValueDict

from sandwich.core.widgets import MultiSelectWidget


class TestMultiSelectWidget:
    """Tests for MultiSelectWidget."""

    def test_renders_as_native_select_multiple(self) -> None:
        """Test that widget renders as native select"""
        choices = [("1", "Option 1"), ("2", "Option 2"), ("3", "Option 3")]
        widget = MultiSelectWidget(choices=choices, attrs={"label": "Test Field"})

        context = widget.get_context(
            name="test_field",
            value=["1", "3"],
            attrs={"label": "Test Field"},
        )

        # Check that value is preserved as a list
        assert context["widget"]["value"] == ["1", "3"]

    def test_handles_none_value(self) -> None:
        """Test that widget handles None value correctly."""
        choices = [("1", "Option 1")]
        widget = MultiSelectWidget(choices=choices)

        context = widget.get_context(name="test_field", value=None, attrs=None)

        # None should be converted to empty list
        assert context["widget"]["value"] == []

    def test_handles_single_string_value(self) -> None:
        """Test that widget converts single string to list."""
        choices = [("1", "Option 1")]
        widget = MultiSelectWidget(choices=choices)

        context = widget.get_context(name="test_field", value="1", attrs=None)

        # Single value should be wrapped in list
        assert context["widget"]["value"] == ["1"]

    def test_value_from_datadict_with_getlist(self) -> None:
        """Test extraction of values from QueryDict-like object."""
        widget = MultiSelectWidget()
        data = QueryDict("field=1&field=2&field=3")
        files: MultiValueDict = MultiValueDict()

        result = widget.value_from_datadict(data, files, "field")

        assert result == ["1", "2", "3"]

    def test_preserves_custom_attrs(self) -> None:
        """Test that widget preserves custom attributes."""
        widget = MultiSelectWidget(choices=[("1", "Option 1")], attrs={"class": "custom-class", "data-foo": "bar"})

        context = widget.get_context(name="test_field", value=None, attrs=None)

        assert "custom-class" in context["widget"]["attrs"].get("class", "")
        assert context["widget"]["attrs"].get("data-foo") == "bar"
