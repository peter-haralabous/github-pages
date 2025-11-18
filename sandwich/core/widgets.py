from typing import Any

from django import forms


class SelectWidget(forms.Select):
    """Widget that renders a native select element with Choices.js enhancement."""

    template_name = "templates/tailwind/layout/select.html"

    def __init__(self, choices: Any = None, attrs: dict[str, Any] | None = None) -> None:
        if attrs is None:
            attrs = {}
        attrs.setdefault("class", "form-select")
        super().__init__(attrs, choices)


class MultiSelectWidget(forms.SelectMultiple):
    """Widget that renders a native select multiple element with Choices.js enhancement."""

    template_name = "widgets/multi_select.html"

    def __init__(self, choices: Any = None, attrs: dict[str, Any] | None = None) -> None:
        if attrs is None:
            attrs = {}
        attrs["multiple"] = "multiple"
        attrs.setdefault("class", "form-select")
        super().__init__(attrs, choices)

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        """Build context for rendering the template."""
        context = super().get_context(name, value, attrs)

        if value is None:
            value = []
        elif not isinstance(value, (list, tuple)):
            value = [value]

        context["widget"]["value"] = value
        return context
