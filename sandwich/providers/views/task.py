import logging
from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.decorators import surveyjs_csp
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task
from sandwich.core.models.task import terminal_task_status
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@surveyjs_csp
@login_required
@authorize_objects(
    [
        ObjPerm(Task, "task_id", ["view_task"]),
        ObjPerm(Organization, "organization_id", ["view_organization"]),
        ObjPerm(Patient, "patient_id", ["view_patient"]),
    ]
)
def task(request: AuthenticatedHttpRequest, organization: Organization, patient: Patient, task: Task) -> HttpResponse:
    logger.info(
        "Accessing patient task", extra={"user_id": request.user.id, "patient_id": patient.id, "task_id": task.id}
    )

    # NOTE-NG: we're using the task ID here as the form name
    # patients don't have permission to load arbitrary forms
    read_only = terminal_task_status(task.status)
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

    # Check if this is a tab request (embedded in patient details page)
    in_tab = request.GET.get("tab") == "true"

    # Use unique IDs for JSON script elements to avoid conflicts when multiple forms are open
    task_id_str = str(task.id).replace("-", "")
    schema_id = f"form_schema_{task_id_str}"
    data_id = f"initial_data_{task_id_str}"

    # For tab requests, we stay on the patient details page after completion
    complete_url = reverse("providers:patient", kwargs={"organization_id": organization.id, "patient_id": patient.id})

    if in_tab:
        return render(
            request,
            "provider/partials/patient_task_content.html",
            context={
                "organization": organization,
                "patient": patient,
                "task": task,
                "form_schema": form_schema,
                "initial_data": initial_data,
                "read_only": read_only,
                "submit_url": submit_url,
                "save_draft_url": save_draft_url,
                "complete_url": complete_url,
                "schema_id": schema_id,
                "data_id": data_id,
            },
        )

    return render(
        request,
        "provider/task.html",
        context={
            "organization": organization,
            "patient": patient,
            "task": task,
            "form_schema": form_schema,  # could be removed if we offload to api
            "initial_data": initial_data,
            "read_only": read_only,
            "submit_url": submit_url,
            "save_draft_url": save_draft_url,
        },
    )
