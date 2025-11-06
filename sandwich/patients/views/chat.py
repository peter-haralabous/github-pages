from crispy_forms.helper import FormHelper
from django import forms

from sandwich.core.inputs import RoundIconButton
from sandwich.users.models import User


class ChatForm(forms.Form):
    message = forms.CharField(
        required=True, widget=forms.Textarea(attrs={"placeholder": "Ask a question or add notes..."})
    )

    def __init__(self, *args, user: User, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.add_input(
            RoundIconButton(
                icon="arrow-up",
            )
        )
