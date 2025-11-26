import logging
from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from pydantic import BaseModel

from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.condition import ConditionStatus
from sandwich.core.models.health_record import HealthRecord
from sandwich.core.validators.date_time import not_in_future

logger = logging.getLogger(__name__)


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
        is_new_record = self.instance.pk is None
        was_unattested = self.instance.unattested if not is_new_record else False

        instance = super().save(commit=False)
        instance.unattested = False  # the user is either correcting or confirming an unattested record
        if patient is not None:
            instance.patient = patient

        if commit:
            instance.save()

            # Log after successful save
            logger.info(
                "Health record saved",
                extra={
                    "record_type": instance.__class__.__name__,
                    "record_id": instance.pk,
                    "patient_id": instance.patient.id,
                    "is_new": is_new_record,
                    "was_unattested": was_unattested,
                    "attested": not instance.unattested,
                },
            )

        return instance

    @classmethod
    def verbose_name(cls) -> str:
        # https://docs.djangoproject.com/en/5.2/ref/models/options/#verbose-name
        # encapsulated here to avoid lint exclusions everywhere it's called
        return cls.Meta.model._meta.verbose_name  # type: ignore[attr-defined] # noqa: SLF001

    @staticmethod
    def pydantic_schema() -> type[BaseModel]:
        """Return a pydantic schema for the form's arguments.

        This will define the interface for tools for creating or updating health records.
        """
        raise NotImplementedError("Subclasses must implement pydantic_schema")


class ConditionForm(HealthRecordForm[Condition]):
    class Meta:
        model = Condition
        fields = ("name", "status", "onset", "abatement")

    @staticmethod
    def pydantic_schema() -> type[BaseModel]:
        class ConditionFormSchema(BaseModel):
            name: str
            status: ConditionStatus
            onset: date | None = None
            abatement: date | None = None

        return ConditionFormSchema


class DocumentForm(HealthRecordForm[Document]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            "original_filename",
            HTML("""
            {% load lucide %}
            <div class="-mt-2 pb-2 text-xs text-blue-600">
                <a target="_blank" href="{% url "patients:document_download" instance.pk %}">
                    View file {% lucide "external-link" size=12 class="inline align-top" %}
                </a>
            </div>
            """),
            "content_type",
            "size",
            "date",
            "category",
        )

        for field in ("original_filename", "content_type", "size"):
            self.fields[field].disabled = True

    class Meta:
        model = Document
        fields = ("original_filename", "content_type", "size", "date", "category")

    @staticmethod
    def pydantic_schema() -> type[BaseModel]:
        """Document isn't a part of the LLM tools yet; need an exact use case to figure out the interface"""
        raise NotImplementedError("Document doesn't do this yet")


class ImmunizationForm(HealthRecordForm[Immunization]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].validators.append(not_in_future)
        self.fields["date"].widget = forms.DateInput(attrs={"type": "date"})

    class Meta:
        model = Immunization
        fields = ("name", "date")

    @staticmethod
    def pydantic_schema() -> type[BaseModel]:
        class ImmunizationFormSchema(BaseModel):
            name: str
            date: date

        return ImmunizationFormSchema


class PractitionerForm(HealthRecordForm[Practitioner]):
    class Meta:
        model = Practitioner
        fields = ("name",)

    @staticmethod
    def pydantic_schema() -> type[BaseModel]:
        class PractitionerFormSchema(BaseModel):
            name: str

        return PractitionerFormSchema
