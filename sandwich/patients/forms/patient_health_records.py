from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.health_record import HealthRecord
from sandwich.core.validators.date_time import not_in_future


class HealthRecordForm[M: HealthRecord](forms.ModelForm[M]):
    def __init__(self, *args, show_delete: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        if self.instance and self.instance.unattested:
            pass  # should the button text change? or add a second button for "looks good"?
        self.helper.add_input(Submit("submit", "Submit"))
        if show_delete:
            # NOTE-NG: hx-confirm doesn't do anything unless we attach custom hx-post behaviour to this button.
            #          if it inherits the form's hx-post the confirmation dialog isn't shown.
            self.helper.add_input(
                Submit(
                    "delete",
                    "Delete",
                    css_class="!btn-error",
                    hx_delete=self.instance.get_absolute_url(),
                    hx_confirm="Are you sure?",
                )
            )

    # NOTE: patient is marked as optional here to prevent mypy from complaining that the signature is incompatible
    #       with the base class, but a database constraint will prevent the form from being submitted without a patient
    def save(self, commit: bool = True, patient: Patient | None = None) -> M:  # noqa: FBT001,FBT002
        instance = super().save(commit=False)
        instance.unattested = False  # the user is either correcting or confirming an unattested record
        if patient is not None:
            instance.patient = patient
        if commit:
            instance.save()
        return instance

    @classmethod
    def verbose_name(cls) -> str:
        # https://docs.djangoproject.com/en/5.2/ref/models/options/#verbose-name
        # encapsulated here to avoid lint exclusions everywhere it's called
        return cls.Meta.model._meta.verbose_name  # type: ignore[attr-defined] # noqa: SLF001


class ConditionForm(HealthRecordForm[Condition]):
    class Meta:
        model = Condition
        fields = ("name", "status", "onset", "abatement")


class DocumentForm(HealthRecordForm[Document]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in ("original_filename", "content_type", "size"):
            self.fields[field].disabled = True

    class Meta:
        model = Document
        fields = ("original_filename", "content_type", "size", "date", "category")


class ImmunizationForm(HealthRecordForm[Immunization]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].validators.append(not_in_future)
        self.fields["date"].widget = forms.DateInput(attrs={"type": "date"})

    class Meta:
        model = Immunization
        fields = ("name", "date")


class PractitionerForm(HealthRecordForm[Practitioner]):
    class Meta:
        model = Practitioner
        fields = ("name",)
