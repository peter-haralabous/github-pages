import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

logger = logging.getLogger(__name__)


class DeleteConfirmationForm(forms.Form):
    confirmation = forms.CharField(
        max_length=6, label="", widget=forms.TextInput(attrs={"placeholder": "Type 'DELETE' to confirm"})
    )

    def __init__(self, *args, **kwargs) -> None:
        form_action = kwargs.pop("form_action", "")

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Delete"))

        if form_action:
            self.helper.form_action = form_action

    def clean_confirmation(self):
        confirmation = self.cleaned_data["confirmation"]

        if confirmation != "DELETE":
            raise forms.ValidationError("Must type 'DELETE' to confirm.")  # noqa: EM101

        return confirmation
