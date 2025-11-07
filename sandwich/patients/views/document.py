import logging

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.datastructures import MultiValueDict
from django.views.decorators.http import require_POST
from guardian.shortcuts import get_objects_for_user
from private_storage.views import PrivateStorageDetailView

from config.settings.base import FEATURE_PATIENT_CHATTY_APP
from sandwich.core.models.document import Document
from sandwich.core.models.patient import Patient
from sandwich.core.service.document_service import assign_default_document_permissions
from sandwich.core.service.ingest_service import process_document_job
from sandwich.core.service.ingest_service import send_ingest_progress
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


class DocumentDownloadView(PrivateStorageDetailView):
    model = Document  # type: ignore[assignment]
    model_file_field = "file"
    pk_url_kwarg = "document_id"

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Document.objects.none()

        # I can only download files for my patients
        authorized_documents = get_objects_for_user(self.request.user, ["view_document"], super().get_queryset())
        return authorized_documents.filter(patient__in=self.request.user.patient_set.all())

    def can_access_file(self, private_file):
        return True


document_download = login_required(DocumentDownloadView.as_view())

SUPPORTED_FILE_TYPES = ["application/pdf", "text/plain"]


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ("file", "patient", "encounter")

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if getattr(file, "content_type", None) not in SUPPORTED_FILE_TYPES:
            msg = "Unsupported file type."
            raise forms.ValidationError(msg)
        return file

    def save(self, commit=True):  # noqa: FBT002
        instance = super().save(commit=False)
        file = self.cleaned_data.get("file")
        if file:
            instance.content_type = getattr(file, "content_type", "")
            instance.size = getattr(file, "size", None)
            instance.original_filename = getattr(file, "name", "")
        if commit:
            instance.save()
        return instance


@require_POST
@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "create_document"])])
def document_upload_and_extract(request: AuthenticatedHttpRequest, patient: Patient):
    files = request.FILES.getlist("file")
    for file in files:
        form = DocumentForm({"patient": patient.id}, MultiValueDict({"file": [file]}))
        if form.is_valid():
            document = form.save()
            assign_default_document_permissions(document)
            try:
                process_document_job.defer(document_id=str(document.id))
                send_ingest_progress(patient.id, text=f"Uploaded {document.original_filename}...")
            except RuntimeError:
                logger.warning("Failed to enqueue document analysis", exc_info=True)
                messages.add_message(request, messages.ERROR, "Failed to enqueue document analysis")
        else:
            logger.info("Invalid document upload form")
            error = ", ".join([str(e) for e in form.errors.get("file", [])])
            messages.add_message(request, messages.ERROR, f"Failed to upload document: {error}")

    if FEATURE_PATIENT_CHATTY_APP:
        return render(request, "partials/messages_oob.html")

    documents = patient.document_set.all()
    return render(request, "patient/partials/documents_table.html", {"documents": documents})


@require_POST
@login_required
@authorize_objects(
    [
        ObjPerm(Patient, "patient_id", ["view_patient"]),
        ObjPerm(Document, "document_id", ["view_document", "delete_document"]),
    ]
)
def document_delete(request: AuthenticatedHttpRequest, patient: Patient, document: Document):
    document.delete()
    documents = patient.document_set.all()
    return render(request, "patient/partials/documents_table.html", {"documents": documents})
