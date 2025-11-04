import logging
import uuid
from typing import Annotated
from typing import cast

import ninja
from django.http import JsonResponse
from ninja.errors import HttpError
from ninja.security import SessionAuth

from sandwich.core.models.form_submission import FormSubmission
from sandwich.core.models.form_submission import FormSubmissionStatus
from sandwich.core.models.task import Task
from sandwich.core.service.permissions_service import get_authorized_object_or_404
from sandwich.core.service.task_service import complete_task
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)
router = ninja.Router()
require_login = SessionAuth()


def get_form_for_task(task: Task):
    return task.form_version.schema if task.form_version else {}


@router.get("/{task_id}", auth=require_login)
def get_form(request: AuthenticatedHttpRequest, task_id: uuid.UUID):
    task = cast("Task", get_authorized_object_or_404(request.user, ["view_task"], Task, id=task_id))
    return get_form_for_task(task)


@router.post("/{task_id}/submit", auth=require_login)
def submit_form(request: AuthenticatedHttpRequest, task_id: uuid.UUID, payload: Annotated[dict, ninja.Body(...)]):
    task = cast("Task", get_authorized_object_or_404(request.user, ["view_task", "complete_task"], Task, id=task_id))

    submission, _ = FormSubmission.objects.get_or_create(
        task=task,
        patient=task.patient,
        defaults={
            "form_version": task.form_version,
            "status": FormSubmissionStatus.DRAFT,
        },
    )

    # checks if submission is already completed
    if submission.status == FormSubmissionStatus.COMPLETED:
        raise HttpError(400, "This form has already been submitted")

    try:
        # extract data, save submission, task gets changed to completed
        submission.data = payload.get("data", submission.data)
        submission.submit()
        complete_task(task)
        logger.debug(
            "Form submission submitted",
            extra={
                "user_id": request.user.id,
                "patient_id": task.patient,
                "task_id": task.id,
                "submission_status": submission.status,
            },
        )
        return JsonResponse(
            {"status": "success", "message": "Form submitted successfully", "submitted_at": submission.submitted_at}
        )

    except Exception as e:
        logger.exception("Error submitting form: {e}")
        raise HttpError(500, "An unexpected error occured.") from e
