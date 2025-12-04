import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from sandwich.core.models import Patient
from sandwich.core.models.task import ACTIVE_TASK_STATUSES
from sandwich.core.service.health_record_service import get_total_health_record_count
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.views.patient import _chat_context

logger = logging.getLogger(__name__)


def _chatty_patient_details_context(request: AuthenticatedHttpRequest, patient: Patient):
    records_count = get_total_health_record_count(patient)
    repository_count = patient.document_set.count()
    tasks_count = patient.task_set.filter(status__in=ACTIVE_TASK_STATUSES).count()

    return {
        "records_count": records_count,
        "repository_count": repository_count,
        "tasks_count": tasks_count,
    } | _chat_context(request, patient=patient)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def patient_details(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    template = "patient/chatty/app.html"
    context = _chatty_patient_details_context(request, patient)

    if request.headers.get("HX-Target") == "left-panel":
        template = "patient/chatty/partials/left_panel.html"

    return render(request, template, context)
