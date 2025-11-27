import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.forms import DeleteConfirmationForm
from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Immunization
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.service.ingest_service import process_document_job
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import htmx_redirect
from sandwich.core.validators.phn import phn_attr_for_province
from sandwich.patients.forms.patient_edit import PatientEdit
from sandwich.patients.views.patient import _patient_context

logger = logging.getLogger(__name__)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"])])
def patient_edit(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    logger.info("Accessing patient edit", extra={"user_id": request.user.id, "patient_id": patient.id})

    if request.method == "POST":
        logger.info("Processing patient edit form", extra={"user_id": request.user.id, "patient_id": patient.id})
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            logger.info("Patient updated successfully", extra={"user_id": request.user.id, "patient_id": patient.id})
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(reverse("patients:patient_edit", kwargs={"patient_id": patient.id}))
        logger.warning(
            "Invalid patient edit form",
            extra={"user_id": request.user.id, "patient_id": patient.id, "form_errors": list(form.errors.keys())},
        )
    else:
        logger.debug("Rendering patient edit form", extra={"user_id": request.user.id, "patient_id": patient.id})
        form = PatientEdit(instance=patient)

    context = {"form": form} | _patient_context(request, patient=patient)
    return render(request, "patient/patient_edit.html", context)


@login_required
def get_phn_validation(request: AuthenticatedHttpRequest) -> HttpResponse:
    province = request.GET.get("province")

    # Note: being used for patient add/onbboarding, might have to change
    form = PatientEdit()

    attrs = phn_attr_for_province(province)

    # Update the attributes on the form
    form.fields["phn"].widget.attrs.update(attrs)

    logger.debug(
        "Phn pattern results",
        extra={"user_id": request.user.id, "attrs": form.fields["phn"].widget.attrs},
    )

    return render(request, "patient/partials/phn_input.html", {"form": form})


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"])])
def patient_delete_health_records(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    """Delete all health records for a patient, including documents."""
    form_action = reverse("patients:patient_delete_health_records", kwargs={"patient_id": patient.id})

    if request.method == "POST":
        logger.info("Processing health records deletion", extra={"user_id": request.user.id, "patient_id": patient.id})
        form = DeleteConfirmationForm(request.POST, form_action=form_action, hx_target="dialog")
        if form.is_valid():
            with transaction.atomic():
                # Delete all health records (includes documents, conditions, immunizations, practitioners)
                Document.objects.filter(patient=patient).delete()
                Condition.objects.filter(patient=patient).delete()
                Immunization.objects.filter(patient=patient).delete()
                Practitioner.objects.filter(patient=patient).delete()

                logger.info(
                    "All health records deleted successfully",
                    extra={"user_id": request.user.id, "patient_id": patient.id},
                )
            messages.add_message(request, messages.SUCCESS, "All health records have been deleted successfully.")
            return htmx_redirect(request, reverse("patients:patient_edit", kwargs={"patient_id": patient.id}))
        context = {"form": form, "patient": patient}
        return render(request, "patient/partials/delete_health_records_modal.html", context)
    form = DeleteConfirmationForm(form_action=form_action, hx_target="dialog")

    context = {"form": form, "patient": patient}
    return render(request, "patient/partials/delete_health_records_modal.html", context)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"])])
def patient_delete_and_reprocess(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    form_action = reverse("patients:patient_delete_and_reprocess", kwargs={"patient_id": patient.id})
    if request.method == "POST":
        logger.info(
            "Processing health records deletion and reprocessing",
            extra={"user_id": request.user.id, "patient_id": patient.id},
        )
        form = DeleteConfirmationForm(request.POST, form_action=form_action, hx_target="dialog")
        if form.is_valid():
            with transaction.atomic():
                # Delete non-document health records
                Condition.objects.filter(patient=patient).delete()
                Immunization.objects.filter(patient=patient).delete()
                Practitioner.objects.filter(patient=patient).delete()

                # Queue all documents for re-processing
                documents = Document.objects.filter(patient=patient)
                document_count = documents.count()

                for document in documents:
                    process_document_job.defer(document_id=str(document.id))

                logger.info(
                    "Health records deleted and documents queued for reprocessing",
                    extra={
                        "user_id": request.user.id,
                        "patient_id": patient.id,
                        "document_count": document_count,
                    },
                )

            messages.add_message(
                request,
                messages.SUCCESS,
                f"Health records deleted and {document_count} document(s) queued for re-processing.",
            )
            return htmx_redirect(request, reverse("patients:patient_edit", kwargs={"patient_id": patient.id}))
        context = {"form": form, "patient": patient}
        return render(request, "patient/partials/delete_and_reprocess_modal.html", context)
    form = DeleteConfirmationForm(
        form_action=reverse("patients:patient_delete_and_reprocess", kwargs={"patient_id": patient.id}),
        hx_target="dialog",
    )
    context = {"form": form, "patient": patient}
    return render(request, "patient/partials/delete_and_reprocess_modal.html", context)
