from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

_blank_link = '<a class="link" target="_blank" href="%s">%s</a>'


class PatientConsentForm(forms.Form):
    required = forms.BooleanField(
        required=True,
        label="",  # will be set in __init__
        help_text="I consent to the use of my health data to power the features within this application.",
    )
    marketing = forms.BooleanField(
        required=False,
        label="Stay up to date (Optional)",
        help_text="Receive occasional emails such as updates on features, tips, and promotional content",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tos_link = _blank_link % (
            reverse("core:policy_detail", args=["terms-of-use"]),
            "Terms of Use",
        )
        privacy_link = _blank_link % (
            reverse("core:policy_detail", args=["privacy-notice"]),
            "Privacy Policy",
        )
        self.fields["required"].label = mark_safe(f"I agree to the {tos_link} and {privacy_link}")  # noqa: S308
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("continue", "Continue", css_class="btn btn-primary w-full"))
        self.helper.field_template = "form/field.html"  # type: ignore[assignment]
