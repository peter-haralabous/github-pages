from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import Layout
from django import forms


class InlineEditForm(forms.Form):
    """Form for inline editing of encounter fields."""

    value = forms.CharField(required=False)

    def __init__(
        self,
        *args,
        field_type: str,
        field_name: str,
        form_action: str,
        current_value: str | None = None,
        choices: list[tuple[str, str]] | None = None,
        **kwargs,
    ) -> None:
        hx_target = kwargs.pop("hx_target", None)
        super().__init__(*args, **kwargs)

        if field_type == "select":
            self.fields["value"] = forms.ChoiceField(
                choices=choices or [],
                required=False,
                widget=forms.Select(
                    attrs={
                        "class": "select select-sm select-bordered inline-edit-select w-full",
                        "autofocus": True,
                        "data-auto-open": "true",
                        "aria-label": field_name,
                    }
                ),
            )
            if current_value:
                self.initial["value"] = current_value
        elif field_type == "date":
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
