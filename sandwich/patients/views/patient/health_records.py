import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from sandwich.core.models import Document
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.health_record import HealthRecord
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.validators.date_time import not_in_future
from sandwich.patients.views.patient import _patient_context
from sandwich.users.models import User

logger = logging.getLogger(__name__)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def health_records(request: AuthenticatedHttpRequest, patient: Patient):
    documents = patient.document_set.all()
    immunizations = patient.immunization_set.all()
    practitioners = patient.practitioner_set.all()

    context = {
        "patient": patient,
        "documents": documents,
        "immunizations": immunizations,
        "practitioners": practitioners,
    } | _patient_context(request, patient=patient)
    return render(request, "patient/health_records.html", context)


class HealthRecordForm[M: HealthRecord](forms.ModelForm[M]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        if self.instance and self.instance.unattested:
            pass  # should the button text change? or add a second button for "looks good"?
        self.helper.add_input(Submit("submit", "Submit"))

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


class ImmunizationForm(HealthRecordForm[Immunization]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].validators.append(not_in_future)

    class Meta:
        model = Immunization
        fields = ("name", "date")


class PractitionerForm(HealthRecordForm[Practitioner]):
    class Meta:
        model = Practitioner
        fields = ("name",)


class DocumentForm(HealthRecordForm[Document]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in ("original_filename", "content_type", "size"):
            self.fields[field].disabled = True

    class Meta:
        model = Document
        fields = ("original_filename", "content_type", "size", "date", "category")


def _form_class(record_type: str):
    if record_type == "immunization":
        return ImmunizationForm
    if record_type == "practitioner":
        return PractitionerForm
    if record_type == "document":
        return DocumentForm
    raise Http404(f"Unknown form class: {record_type}")


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"])])
def health_records_add(request: AuthenticatedHttpRequest, patient: Patient, record_type: str):
    form_class = _form_class(record_type)
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save(patient=patient)
            return HttpResponseRedirect(reverse("patients:health_records", kwargs={"patient_id": patient.id}))
    else:
        form = form_class()

    context = {
        "record_type": record_type,
        "record_type_name": form_class.Meta.model._meta.verbose_name,  # noqa: SLF001
        "form": form,
    } | _patient_context(request, patient=patient)
    return render(request, "patient/health_records_add.html", context)


@dataclass
class HistoryEvent:
    label: str
    date: datetime
    actor: str

    def get_label_display(self):
        if self.label == "insert":
            return _("Added")
        if self.label == "update":
            return _("Updated")
        if self.label == "delete":
            return _("Deleted")
        return self.label.replace("_", " ").title()

    @staticmethod
    def _actor_label(current_user: User, metadata: dict[str, Any]):
        user_id = metadata.get("user")
        if user_id is None:
            # which model was used is useful internally but shouldn't be shown to the user
            llm = metadata.get("llm")
            if llm:
                return _("Thrive AI Assistant")
            return _("Unknown")
        if user_id == current_user.id:
            return current_user.email
        # TODO-NG: Figure out our permissions story here. We shouldn't leak user email addresses, but we do need
        #          to give the user *some* information about who's been updating their records.
        return _("User %s") % user_id

    @classmethod
    def from_event(cls, current_user: User, event):
        metadata = event.pgh_context.metadata if event.pgh_context else {}
        return cls(
            label=event.pgh_label,
            date=event.pgh_created_at,
            actor=cls._actor_label(current_user, metadata),
        )


def _history_events(instance: HealthRecord, user: User) -> list[HistoryEvent]:
    return [
        HistoryEvent.from_event(user, event)
        for event in instance.events.prefetch_related("pgh_context").order_by("-pgh_created_at")
    ]


def _generic_edit_view(record_type: str, request: AuthenticatedHttpRequest, instance: HealthRecord):
    patient = instance.patient
    if not request.user.has_perms(["view_patient", "change_patient"], instance.patient):
        # this is the same error that get_object_or_404 raises
        raise Http404(f"No {instance._meta.object_name} matches the given query.")  # noqa: SLF001

    form_class = _form_class(record_type)
    if request.method == "DELETE":
        instance.delete()
        if request.headers.get("HX-Request") == "true":
            # FIXME: doing row-by-row deletes means removing the last row doesn't re-add the empty state
            #        consider re-rendering the entire table instead, like how document_delete does it
            return HttpResponse(status=200)
        return HttpResponseRedirect(reverse("patients:health_records", kwargs={"patient_id": patient.id}))
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save(patient=patient)
            return HttpResponseRedirect(reverse("patients:health_records", kwargs={"patient_id": patient.id}))
    else:
        form = form_class(instance=instance)

    context = {
        "record_type": record_type,
        "record_type_name": form_class.Meta.model._meta.verbose_name,  # noqa: SLF001
        "form": form,
        "history": _history_events(instance, request.user),
    } | _patient_context(request, patient=patient)
    return render(request, "patient/health_records_edit.html", context)


@login_required
def immunization_edit(request: AuthenticatedHttpRequest, immunization_id: UUID):
    instance = get_object_or_404(Immunization, id=immunization_id)
    return _generic_edit_view("immunization", request, instance)


@login_required
def practitioner_edit(request: AuthenticatedHttpRequest, practitioner_id: UUID):
    instance = get_object_or_404(Practitioner, id=practitioner_id)
    return _generic_edit_view("practitioner", request, instance)


@login_required
def document_edit(request: AuthenticatedHttpRequest, document_id: UUID):
    instance = get_object_or_404(Document, id=document_id)
    return _generic_edit_view("document", request, instance)
