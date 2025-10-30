import logging
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.decorators import surveyjs_csp
from sandwich.core.models.task import Task
from sandwich.core.models.task import terminal_task_status
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@surveyjs_csp
@login_required
@authorize_objects([ObjPerm(Task, "task_id", ["view_task"])])
def task(request: AuthenticatedHttpRequest, organization_id: UUID, patient_id: UUID, task: Task) -> HttpResponse:
    logger.info(
        "Accessing patient task", extra={"user_id": request.user.id, "patient_id": patient_id, "task_id": task.id}
    )

    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)

    # NOTE-NG: we're using the task ID here as the form name
    # patients don't have permission to load arbitrary forms
    read_only = terminal_task_status(task.status)
    logger.debug(
        "Task form configuration",
        extra={
            "user_id": request.user.id,
            "patient_id": patient_id,
            "task_id": task.id,
            "task_status": task.status.value,
            "read_only": read_only,
            "has_submission": bool(task.formio_submission),
        },
    )

    # no, I don't want to catch RelatedObjectDoesNotExist if there's no submission yet
    if task.formio_submission:
        form_url = request.build_absolute_uri(
            reverse(
                "patients:api-1.0.0:get_formio_form_submission",
                kwargs={"name": str(task.id), "submission_id": str(task.formio_submission.id)},
            )
        )
        logger.debug(
            "Using existing form submission",
            extra={
                "user_id": request.user.id,
                "patient_id": patient_id,
                "task_id": task.id,
                "submission_id": task.formio_submission.id,
            },
        )
    else:
        form_url = request.build_absolute_uri(
            reverse("patients:api-1.0.0:get_formio_form", kwargs={"name": str(task.id)})
        )
        logger.debug(
            "Using new form", extra={"user_id": request.user.id, "patient_id": patient_id, "task_id": task.id}
        )

    formio_user = {"_id": request.user.id}

    form_schema = task.form_version.schema if task.form_version else {}

    return render(
        request,
        "provider/task.html",
        context={
            "organization": organization,
            "patient": patient,
            "task": task,
            "form_schema": form_schema,  # could be removed if we offload to api
            "form_url": form_url,
            "formio_user": formio_user,
            "read_only": read_only,
        },
    )
