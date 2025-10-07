import logging
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.task import terminal_task_status
from sandwich.core.service.organization_service import get_provider_organizations
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def task(request: AuthenticatedHttpRequest, organization_id: UUID, patient_id: UUID, task_id: UUID) -> HttpResponse:
    logger.info(
        "Accessing patient task", extra={"user_id": request.user.id, "patient_id": patient_id, "task_id": task_id}
    )

    organization = get_object_or_404(get_provider_organizations(request.user), id=organization_id)
    patient = get_object_or_404(organization.patient_set, id=patient_id)
    task = get_object_or_404(patient.task_set, id=task_id)

    # NOTE-NG: we're using the task ID here as the form name
    # patients don't have permission to load arbitrary forms
    read_only = terminal_task_status(task.status)
    logger.debug(
        "Task form configuration",
        extra={
            "user_id": request.user.id,
            "patient_id": patient_id,
            "task_id": task_id,
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
                kwargs={"name": str(task_id), "submission_id": str(task.formio_submission.id)},
            )
        )
        logger.debug(
            "Using existing form submission",
            extra={
                "user_id": request.user.id,
                "patient_id": patient_id,
                "task_id": task_id,
                "submission_id": task.formio_submission.id,
            },
        )
    else:
        form_url = request.build_absolute_uri(
            reverse("patients:api-1.0.0:get_formio_form", kwargs={"name": str(task_id)})
        )
        logger.debug(
            "Using new form", extra={"user_id": request.user.id, "patient_id": patient_id, "task_id": task_id}
        )

    formio_user = {"_id": request.user.id}

    return render(
        request,
        "provider/task.html",
        context={
            "organization": organization,
            "patient": patient,
            "task": task,
            "form_url": form_url,
            "formio_user": formio_user,
            "read_only": read_only,
        },
    )
