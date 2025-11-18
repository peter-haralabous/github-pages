from typing import TypedDict

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import Layout
from django import forms

from sandwich.core.widgets import MultiSelectWidget
from sandwich.core.widgets import SelectWidget


class InlineEditForm(forms.Form):
    """Base form for inline editing of encounter fields."""

    value = forms.CharField(required=False)
    field_type: str = "text"

    def __init__(
        self,
        *args,
        field_name: str,
        form_action: str,
        current_value: str | list[str] | None = None,
        **kwargs,
    ) -> None:
        hx_target = kwargs.pop("hx_target", None)
        super().__init__(*args, **kwargs)

        if current_value:
            self.initial["value"] = current_value

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = form_action
        self.helper.form_class = "inline-edit-form"
        self.helper.form_show_labels = False
        self.helper.disable_csrf = False

        self.helper.attrs = {
            "hx-post": form_action,
            "hx-swap": "outerHTML",
            "aria-label": f"Edit {field_name}",
        }
        if hx_target:
            self.helper.attrs["hx-target"] = hx_target

        self.helper.layout = Layout(Div("value", css_class="w-full"))


class InlineEditSelectForm(InlineEditForm):
    """Form for inline editing with a select dropdown."""

    field_type = "select"

    def __init__(
        self,
        *args,
        field_name: str,
        form_action: str,
        current_value: str | None = None,
        choices: list[tuple[str, str]],
        **kwargs,
    ) -> None:
        super().__init__(*args, field_name=field_name, form_action=form_action, current_value=current_value, **kwargs)
        self.fields["value"] = forms.ChoiceField(
            choices=choices,
            required=False,
            widget=SelectWidget(
                choices=choices,
                attrs={
                    "autofocus": True,
                    "allow_clear": True,
                    "label": field_name,
                },
            ),
        )
        if current_value:
            self.initial["value"] = current_value


class InlineEditMultiSelectForm(InlineEditForm):
    """Form for inline editing with a multi-select dropdown."""

    field_type = "multi-select"

    def __init__(
        self,
        *args,
        field_name: str,
        form_action: str,
        current_value: list[str] | str | None = None,
        choices: list[tuple[str, str]],
        **kwargs,
    ) -> None:
        super().__init__(*args, field_name=field_name, form_action=form_action, current_value=current_value, **kwargs)
        self.fields["value"] = forms.MultipleChoiceField(
            choices=choices,
            required=False,
            widget=MultiSelectWidget(
                choices=choices,
                attrs={
                    "autofocus": True,
                    "label": field_name,
                },
            ),
        )
        if current_value:
            self.initial["value"] = current_value if isinstance(current_value, list) else [current_value]


class InlineEditDateForm(InlineEditForm):
    """Form for inline editing with a date input."""

    field_type = "date"

    def __init__(
        self,
        *args,
        field_name: str,
        form_action: str,
        current_value: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, field_name=field_name, form_action=form_action, current_value=current_value, **kwargs)
        self.fields["value"] = forms.DateField(
            required=False,
            widget=forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "input input-sm input-bordered w-full inline-edit-input",
                    "autofocus": True,
                    "aria-label": field_name,
                }
            ),
        )
        if current_value:
            self.initial["value"] = current_value


class FormContext(TypedDict):
    """Type definition for inline edit form context."""

    choices: list[tuple[str, str]]
    current_value: str | list[str] | None
    field_type: str
    field_label: str


def create_inline_edit_form(
    form_context: FormContext,
    field_name: str,
    form_action: str,
    hx_target: str,
    data: dict | None = None,
) -> InlineEditForm:
    """Create the appropriate form class based on field type."""
    field_type = form_context["field_type"]
    choices = form_context["choices"]
    current_value = form_context["current_value"]

    if field_type == "select":
        # For select fields, current_value should be a string or None
        single_value = current_value if isinstance(current_value, str) or current_value is None else None
        return InlineEditSelectForm(
            data,
            field_name=field_name,
            form_action=form_action,
            current_value=single_value,
            choices=choices,
            hx_target=hx_target,
        )
    if field_type == "multi-select":
        multi_value = [current_value] if isinstance(current_value, str) else (current_value or [])
        return InlineEditMultiSelectForm(
            data,
            field_name=field_name,
            form_action=form_action,
            current_value=multi_value,
            choices=choices,
            hx_target=hx_target,
        )
    if field_type == "date":
        date_value = current_value if isinstance(current_value, str) or current_value is None else None
        return InlineEditDateForm(
            data,
            field_name=field_name,
            form_action=form_action,
            current_value=date_value,
            hx_target=hx_target,
        )
    return InlineEditForm(
        data,
        field_name=field_name,
        form_action=form_action,
        current_value=current_value,
        hx_target=hx_target,
    )
