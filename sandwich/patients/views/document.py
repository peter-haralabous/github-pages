from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.http import require_POST

from sandwich.core.models.document import Document
from sandwich.core.util.http import AuthenticatedHttpRequest


@require_POST
@login_required
def upload(request: AuthenticatedHttpRequest, patient_id: UUID):
    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"success": False, "error": "No file uploaded."})
    if file.content_type != "application/pdf":
        return JsonResponse({"success": False, "error": "Only PDF files are allowed."})
    Document.objects.create(patient=patient, file=file)
    documents = patient.document_set.all()
    return render(request, "patient/partials/documents_table.html", {"documents": documents})


@require_POST
@login_required
def delete(request: AuthenticatedHttpRequest, patient_id: UUID, document_id: UUID):
    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    document = get_object_or_404(patient.document_set, id=document_id)
    document.delete()
    documents = patient.document_set.all()
    return render(request, "patient/partials/documents_table.html", {"documents": documents})
