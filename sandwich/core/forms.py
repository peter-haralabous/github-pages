import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

logger = logging.getLogger(__name__)


class DeleteConfirmationForm(forms.Form):
    confirmation = forms.CharField(
        max_length=6,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Type 'DELETE' to confirm",
                "autofocus": True,
                "required": "required",
                "pattern": "^DELETE$",
            }
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        form_action = kwargs.pop("form_action", "")
        submit_label = kwargs.pop("submit_label", "Delete")
        hx_target = kwargs.pop("hx_target", None)

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs["hx-post"] = form_action
        self.helper.attrs["hx-trigger"] = "submit"
        self.helper.attrs["hx-swap"] = "outerHTML"

        if hx_target:
            self.helper.attrs["hx-target"] = hx_target

        self.helper.add_input(Submit("submit", submit_label, css_class="!btn-error"))

        if form_action:
            self.helper.form_action = form_action

    def clean_confirmation(self):
        confirmation = self.cleaned_data["confirmation"]

        if confirmation != "DELETE":
            raise forms.ValidationError("Must type 'DELETE' to confirm.")

        return confirmation
