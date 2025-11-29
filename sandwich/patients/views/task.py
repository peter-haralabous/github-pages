import logging
from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.decorators import surveyjs_csp
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.views.patient import _patient_context

logger = logging.getLogger(__name__)


@surveyjs_csp
@login_required
@authorize_objects(
    [
        ObjPerm(Task, "task_id", ["view_task"]),
        ObjPerm(Patient, "patient_id", ["view_patient"]),
    ]
)
def task(request: AuthenticatedHttpRequest, patient: Patient, task: Task) -> HttpResponse:
    logger.info(
        "Accessing patient task", extra={"user_id": request.user.id, "patient_id": patient.id, "task_id": task.id}
    )

    # NOTE-NG: we're using the task ID here as the form name
    # patients don't have permission to load arbitrary forms
    read_only = not task.active
    logger.debug(
        "Task form configuration",
        extra={
            "user_id": request.user.id,
            "patient_id": patient.id,
            "task_id": task.id,
            "task_status": task.status.value,
            "read_only": read_only,
        },
    )

    form_schema = task.form_version.schema if task.form_version else {}
    submit_url = request.build_absolute_uri(
        reverse("patients:patients-api:submit_form", kwargs={"task_id": str(task.id)})
    )
    save_draft_url = request.build_absolute_uri(
        reverse("patients:patients-api:save_draft_form", kwargs={"task_id": str(task.id)})
    )

    initial_data: dict[str, Any] | None = None
    form_submission = task.get_form_submission()
    if form_submission:
        initial_data = form_submission.data

    context = {
        "form_schema": form_schema,
        "initial_data": initial_data,
        "submit_url": submit_url,
        "save_draft_url": save_draft_url,
        "read_only": read_only,
        "task": task,
        "address_autocomplete_url": reverse("core:address_search"),
        "medications_autocomplete_url": reverse("core:medication_search"),
    } | _patient_context(request, patient)
    return render(request, "patient/form.html", context=context)
