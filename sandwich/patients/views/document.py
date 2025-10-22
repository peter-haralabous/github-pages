from uuid import UUID

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.http import require_POST
from private_storage.views import PrivateStorageDetailView

from sandwich.core.models.document import Document
from sandwich.core.service.procrastinate_service import extract_facts_from_pdf_job
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


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ("file", "patient", "encounter")

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if getattr(file, "content_type", None) != "application/pdf":
            msg = "Only PDF files are supported."
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
def document_upload_and_extract(request: AuthenticatedHttpRequest, patient_id: UUID):
    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    form = DocumentForm({"patient": patient.id}, request.FILES)
    if form.is_valid():
        document = form.save()
        if document.content_type == "application/pdf":
            try:
                # enqueue background extraction task
                extract_facts_from_pdf_job.defer(document_id=str(document.id))
            except RuntimeError as e:
                messages.add_message(request, messages.ERROR, f"PDF ingestion failed: {e}")
    else:
        error = ", ".join([str(e) for e in form.errors.get("file", [])])
        messages.add_message(request, messages.ERROR, f"Failed to upload document: {error}")
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
