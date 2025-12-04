import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Literal
from typing import cast
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

from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models import Task
from sandwich.core.models.document import DocumentCategory
from sandwich.core.models.health_record import HealthRecord
from sandwich.core.models.health_record import HealthRecordType
from sandwich.core.models.task import ACTIVE_TASK_STATUSES
from sandwich.core.service.health_record_service import get_document_count_by_category
from sandwich.core.service.health_record_service import get_health_record_count_by_type
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.validators.date_time import not_in_future
from sandwich.patients.views.patient import _chat_context
from sandwich.patients.views.patient.details import _chatty_patient_details_context
from sandwich.users.models import User

logger = logging.getLogger(__name__)


@dataclass
class NavItem:
    type = "nav-item"

    link: str
    label: str
    icon: str
    count: int | None = None
    target: Literal["left_panel", "modal"] | None = None


@dataclass
class NavGroup:
    type = "nav-group"

    label: str


RECORD_TYPES = {
    HealthRecordType.CONDITION: (Condition, "heart"),
    HealthRecordType.IMMUNIZATION: (Immunization, "syringe"),
    HealthRecordType.PRACTITIONER: (Practitioner, "contact"),
}


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def patient_records(request: AuthenticatedHttpRequest, patient: Patient, record_type: HealthRecordType | None = None):
    if record_type is None:
        counts = get_health_record_count_by_type(patient)
        left_panel_title = "Records"
        left_panel_back_link = reverse("patients:patient_details", kwargs={"patient_id": patient.id})
        items = [
            NavItem(
                link=reverse(
                    "patients:patient_records",
                    kwargs={"patient_id": patient.id, "record_type": model._meta.model_name},  # noqa: SLF001
                ),
                label=str(model._meta.verbose_name_plural).capitalize(),  # noqa: SLF001
                icon=icon,
                count=counts.get(cast("str", model._meta.model_name), 0),  # noqa: SLF001
                target="left_panel",
            )
            for model, icon in RECORD_TYPES.values()
        ]
    elif record_type not in RECORD_TYPES:
        raise Http404(f"Unknown record type: {record_type}")
    else:
        model, icon = RECORD_TYPES[record_type]
        left_panel_title = str(model._meta.verbose_name_plural).capitalize()  # noqa: SLF001
        left_panel_back_link = reverse("patients:patient_records", kwargs={"patient_id": patient.id})
        items = [
            NavItem(
                link=record.get_absolute_url(),
                label=str(record),
                icon=icon,
                target="modal",
            )
            # FIXME: need to page this list
            for record in model.objects.filter(patient=patient).all()  # type: ignore[attr-defined]
        ]
        items.insert(
            0,
            NavItem(
                link=reverse(
                    "patients:health_records_add", kwargs={"patient_id": patient.id, "record_type": record_type}
                ),
                label="Add New",
                icon="plus",
                target="modal",
            ),
        )

    context = {
        "patient": patient,
        "left_panel_title": left_panel_title,
        "left_panel_back_link": left_panel_back_link,
        "left_panel_items": items,
    }
    if request.headers.get("HX-Target") == "left-panel":
        return render(request, "patient/chatty/partials/left_panel_records.html", context)

    context |= _chat_context(request, patient=patient)
    return render(request, "patient/chatty/records.html", context)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def patient_repository(request: AuthenticatedHttpRequest, patient: Patient, category: str | None = None):
    if category is None:
        counts = get_document_count_by_category(patient)
        left_panel_title = "Repository"
        left_panel_back_link = reverse("patients:patient_details", kwargs={"patient_id": patient.id})
        items = [
            NavItem(
                link=reverse("patients:patient_repository", kwargs={"patient_id": patient.id, "category": value}),
                label=str(label),
                icon="folder",
                count=counts.get(value, 0),
                target="left_panel",
            )
            for (value, label) in DocumentCategory.choices
        ]
    else:
        category = DocumentCategory(category)
        left_panel_title = str(category.label)
        left_panel_back_link = reverse("patients:patient_repository", kwargs={"patient_id": patient.id})
        items = [
            NavItem(link=record.get_absolute_url(), label=str(record), icon="file", target="modal")
            # FIXME: need to page this list
            for record in patient.document_set.filter(category=category)
        ]

    context = {
        "patient": patient,
        "left_panel_title": left_panel_title,
        "left_panel_back_link": left_panel_back_link,
        "left_panel_items": items,
    }
    if request.headers.get("HX-Target") == "left-panel":
        return render(request, "patient/chatty/partials/left_panel_records.html", context)

    context |= _chat_context(request, patient=patient)
    return render(request, "patient/chatty/records.html", context)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def patient_tasks(request: AuthenticatedHttpRequest, patient: Patient):
    left_panel_title = "To Do"
    left_panel_back_link = reverse("patients:patient_details", kwargs={"patient_id": patient.id})

    def task_icon(task: Task) -> str:
        if task.active:
            return "clipboard"
        return "clipboard-check"

    active_items = [
        NavItem(link=task.get_absolute_url(), label=task.name, icon=task_icon(task))
        # FIXME: need to page this list
        for task in patient.task_set.filter(status__in=ACTIVE_TASK_STATUSES)
    ]
    completed_items = [
        NavItem(link=task.get_absolute_url(), label=task.name, icon=task_icon(task))
        # FIXME: need to page this list
        for task in patient.task_set.exclude(status__in=ACTIVE_TASK_STATUSES)
    ]
    items: list[NavItem | NavGroup] = []
    if active_items:
        items.append(NavGroup(label="Pending"))
        items.extend(active_items)
    if completed_items:
        items.append(NavGroup(label="Completed"))
        items.extend(completed_items)
    context = {
        "patient": patient,
        "left_panel_title": left_panel_title,
        "left_panel_back_link": left_panel_back_link,
        "left_panel_items": items,
    }
    if request.headers.get("HX-Target") == "left-panel":
        return render(request, "patient/chatty/partials/left_panel_records.html", context)

    context |= _chat_context(request, patient=patient)
    return render(request, "patient/chatty/records.html", context)


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


def _form_class(record_type: HealthRecordType) -> type[HealthRecordForm]:
    if record_type == HealthRecordType.CONDITION:
        return ConditionForm
    if record_type == HealthRecordType.DOCUMENT:
        return DocumentForm
    if record_type == HealthRecordType.IMMUNIZATION:
        return ImmunizationForm
    if record_type == HealthRecordType.PRACTITIONER:
        return PractitionerForm
    raise Http404(f"Unknown form class: {record_type}")


def show_updated_list_of_records(
    request: AuthenticatedHttpRequest, patient: Patient, record_type: HealthRecordType, instance: HealthRecord
) -> HttpResponse:
    """after adding, updating, or deleting a record, show the updated list that record was a member of"""

    if record_type == HealthRecordType.DOCUMENT:
        url = reverse(
            "patients:patient_repository",
            kwargs={"patient_id": patient.id, "category": cast("Document", instance).category},
        )
    else:
        url = reverse("patients:patient_records", kwargs={"patient_id": patient.id, "record_type": record_type})

    # htmx ignores 302 responses, so we need to redirect the browser ourselves
    if request.headers.get("HX-Request"):
        return HttpResponse(headers={"HX-Redirect": url})
    return HttpResponseRedirect(url)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"])])
def health_records_add(request: AuthenticatedHttpRequest, patient: Patient, record_type: HealthRecordType):
    form_class = _form_class(record_type)
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            instance = form.save(patient=patient)
            return show_updated_list_of_records(request, patient, record_type, instance)
    else:
        form = form_class()

    form.helper.form_action = reverse(
        "patients:health_records_add", kwargs={"patient_id": patient.id, "record_type": record_type}
    )
    form.helper.attrs["hx-post"] = form.helper.form_action
    form.helper.attrs["hx-target"] = "closest dialog"
    form.helper.attrs["hx-swap"] = "outerHTML"
    context = {
        "record_type": record_type,
        "record_type_name": form_class.verbose_name(),
        "form": form,
    }

    if request.headers.get("HX-Request") == "true":
        # only render the modal; leave the rest of the page as-is
        return render(request, "patient/partials/health_record_add_modal.html", context)

    # NOTE: we don't know what state the page was in before the modal was opened; assume it was just the
    #       patient details homepage
    context |= _chatty_patient_details_context(request, patient)
    return render(request, "patient/chatty/records_add.html", context)


@dataclass
class HistoryEvent:
    label: str
    date: datetime
    actor: str
    document: Document | None

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
        document_id = metadata.get("document")
        document = Document.objects.filter(id=document_id).first() if document_id else None
        return cls(
            label=event.pgh_label,
            date=event.pgh_created_at,
            actor=cls._actor_label(current_user, metadata),
            document=document,
        )


@dataclass
class MoreHistoryEvents:
    count: int

    def __str__(self):
        return f"{self.count} more..."


def _history_events(instance: HealthRecord, user: User, limit: int = 10) -> list[HistoryEvent | MoreHistoryEvents]:
    events = instance.events.prefetch_related("pgh_context").order_by("-pgh_created_at")[: limit + 1]
    if len(events) > limit:
        total = instance.get_total_versions()
        return [
            *[HistoryEvent.from_event(user, event) for event in events[: limit - 1]],
            MoreHistoryEvents(total - limit),
            HistoryEvent.from_event(
                user, instance.events.prefetch_related("pgh_context").order_by("pgh_created_at").first()
            ),
        ]
    return [HistoryEvent.from_event(user, event) for event in events]


def _generic_edit_view(record_type: HealthRecordType, request: AuthenticatedHttpRequest, instance: HealthRecord):
    patient = instance.patient
    if not request.user.has_perms(["view_patient", "change_patient"], instance.patient):
        # this is the same error that get_object_or_404 raises
        raise Http404(f"No {instance._meta.object_name} matches the given query.")  # noqa: SLF001

    form_class = _form_class(record_type)
    if request.method == "DELETE":
        instance.delete()
        return show_updated_list_of_records(request, patient, record_type, instance)
    if request.method == "POST":
        form = form_class(request.POST, instance=instance, show_delete=True)
        if form.is_valid():
            form.save(patient=patient)
            return show_updated_list_of_records(request, patient, record_type, instance)
    else:
        form = form_class(instance=instance, show_delete=True)

    form.helper.form_action = instance.get_absolute_url()
    form.helper.attrs["hx-post"] = form.helper.form_action
    form.helper.attrs["hx-target"] = "closest dialog"
    form.helper.attrs["hx-swap"] = "outerHTML"
    context = {
        "record_type": record_type,
        "record_type_name": form_class.verbose_name(),
        "form": form,
        "history": _history_events(instance, request.user),
    }

    if request.headers.get("HX-Request") == "true":
        # only render the modal; leave the rest of the page as-is
        return render(request, "patient/partials/health_record_edit_modal.html", context)

    # NOTE: we don't know what state the page was in before the modal was opened; assume it was just the
    #       patient details homepage
    context |= _chatty_patient_details_context(request, patient)
    return render(request, "patient/chatty/records_edit.html", context)


@login_required
def condition_edit(request: AuthenticatedHttpRequest, condition_id: UUID):
    instance = get_object_or_404(Condition, id=condition_id)
    return _generic_edit_view(HealthRecordType.CONDITION, request, instance)


@login_required
def document_edit(request: AuthenticatedHttpRequest, document_id: UUID):
    instance = get_object_or_404(Document, id=document_id)
    return _generic_edit_view(HealthRecordType.DOCUMENT, request, instance)


@login_required
def immunization_edit(request: AuthenticatedHttpRequest, immunization_id: UUID):
    instance = get_object_or_404(Immunization, id=immunization_id)
    return _generic_edit_view(HealthRecordType.IMMUNIZATION, request, instance)


@login_required
def practitioner_edit(request: AuthenticatedHttpRequest, practitioner_id: UUID):
    instance = get_object_or_404(Practitioner, id=practitioner_id)
    return _generic_edit_view(HealthRecordType.PRACTITIONER, request, instance)
