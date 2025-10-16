from typing import cast
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.http import require_POST
from private_storage.views import PrivateStorageDetailView

from sandwich.core.models.document import Document
from sandwich.core.util.http import AuthenticatedHttpRequest


class DocumentDownloadView(PrivateStorageDetailView):
    model = Document  # type: ignore[assignment]
    model_file_field = "file"
    pk_url_kwarg = "document_id"

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Document.objects.none()

        # I can only download files for my patients
        return super().get_queryset().filter(patient__in=self.request.user.patient_set.all())

    def can_access_file(self, private_file):
        return True


document_download = login_required(DocumentDownloadView.as_view())


@require_POST
@login_required
def document_upload(request: AuthenticatedHttpRequest, patient_id: UUID):
    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"success": False, "error": "No file uploaded."})
    if file.content_type != "application/pdf":
        return JsonResponse({"success": False, "error": "Only PDF files are allowed."})
    Document.objects.create(
        patient=patient,
        file=file,
        content_type=file.content_type,
        size=file.size,
        original_filename=cast("str", file.name),
    )
    documents = patient.document_set.all()
    return render(request, "patient/partials/documents_table.html", {"documents": documents})


@require_POST
@login_required
def document_delete(request: AuthenticatedHttpRequest, patient_id: UUID, document_id: UUID):
    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    document = get_object_or_404(patient.document_set, id=document_id)
    document.delete()
    documents = patient.document_set.all()
    return render(request, "patient/partials/documents_table.html", {"documents": documents})
