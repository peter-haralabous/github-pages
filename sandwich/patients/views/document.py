import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.utils.datastructures import MultiValueDict
from django.views.decorators.http import require_POST
from guardian.shortcuts import get_objects_for_user
from private_storage.views import PrivateStorageDetailView

from sandwich.core.models.document import Document
from sandwich.core.models.patient import Patient
from sandwich.core.service.chat_service.chat import ChatContext
from sandwich.core.service.chat_service.event import FileUploadedEvent
from sandwich.core.service.chat_service.event import receive_chat_event
from sandwich.core.service.chat_service.sse import send_records_updated
from sandwich.core.service.document_service import assign_default_document_permissions
from sandwich.core.service.ingest_service import ProcessDocumentContext
from sandwich.core.service.ingest_service import process_document_job
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.forms.document import DocumentForm

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


@require_POST
@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "create_document"])])
def document_upload_and_extract(request: AuthenticatedHttpRequest, patient: Patient):
    files = request.FILES.getlist("file")
    logger.info(
        "Starting document upload",
        extra={
            "patient_id": str(patient.id),
            "file_count": len(files),
            "user_id": str(request.user.id),
        },
    )

    for file in files:
        logger.debug(
            "Processing uploaded file",
            extra={
                "patient_id": str(patient.id),
                "content_type": file.content_type,
                "size_bytes": file.size,
                "user_id": str(request.user.id),
            },
        )

        form = DocumentForm(
            MultiValueDict({**request.POST, "patient": [patient.id]}),  # type: ignore[dict-item]
            MultiValueDict({"file": [file]}),
        )
        if form.is_valid():
            document = form.save()
            assign_default_document_permissions(document)
            transaction.on_commit(lambda: send_records_updated(patient))

            logger.info(
                "Document saved successfully",
                extra={
                    "document_id": str(document.id),
                    "patient_id": str(patient.id),
                    "content_type": document.content_type,
                    "user_id": str(request.user.id),
                },
            )

            document_context = form.cleaned_data.get("context")
            if document_context and document_context == ProcessDocumentContext.PATIENT_CHAT:
                receive_chat_event(
                    FileUploadedEvent(
                        context=ChatContext(patient_id=str(patient.id)),
                        document_id=str(document.id),
                        document_filename=document.original_filename,
                    )
                )

            try:
                process_document_job.defer(document_id=str(document.id), document_context=document_context)
                logger.info(
                    "Document processing job enqueued",
                    extra={
                        "document_id": str(document.id),
                        "patient_id": str(patient.id),
                        "context": form.cleaned_data.get("context"),
                    },
                )
            except RuntimeError:
                logger.warning(
                    "Failed to enqueue document analysis",
                    extra={
                        "document_id": str(document.id),
                        "patient_id": str(patient.id),
                        "user_id": str(request.user.id),
                    },
                    exc_info=True,
                )
                messages.add_message(request, messages.ERROR, "Failed to enqueue document analysis")
        else:
            logger.warning(
                "Invalid document upload form",
                extra={
                    "patient_id": str(patient.id),
                    "errors": form.errors.as_json(),
                    "user_id": str(request.user.id),
                },
            )
            error = ", ".join([str(e) for e in form.errors.get("file", [])])
            messages.add_message(request, messages.ERROR, f"Failed to upload document: {error}")

    return render(request, "partials/messages_oob.html")
