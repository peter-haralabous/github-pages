import json
import logging
from pathlib import Path
from typing import Literal

import ninja
import pydantic
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja.security import SessionAuth

from sandwich.core.models.formio_submission import FormioSubmission
from sandwich.core.models.task import Task
from sandwich.core.service.task_service import complete_task
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)

router = ninja.Router()
require_login = SessionAuth(csrf=False)  # formio doesn't send django csrf tokens


def get_example_form():
    return json.loads((Path(__file__).parent / "formio_example.json").read_bytes())


def get_form_for_task(task: Task):
    return get_example_form()


def get_task(request: AuthenticatedHttpRequest, form_name: str):
    # NOTE-NG: we're using the task ID here as the form name
    # patients don't have permission to load arbitrary forms
    task_id = form_name
    return get_object_or_404(Task.objects.filter(patient__in=request.user.patient_set.all()), id=task_id)


def get_submission(task: Task, submission_id: str) -> FormioSubmission:
    submission = task.formio_submission
    assert submission
    assert submission.id == int(submission_id)
    return submission


type SubmissionState = Literal["submitted", "draft"]


# NOTE-NG: I'm guessing at API shapes based on observed behaviour, N=1
class CreateSubmissionRequest(ninja.Schema):
    model_config = pydantic.ConfigDict(serialize_by_alias=True)

    data: dict
    metadata: dict | None = None  # only set when submitting? sometimes it's omitted, sometimes it's {}
    state: SubmissionState
    # _vnote: Literal[""] # ???


class UpdateSubmissionRequest(CreateSubmissionRequest):
    id: str = ninja.Field(default=None, alias="_id")


class SubmissionResponse(ninja.Schema):
    model_config = pydantic.ConfigDict(serialize_by_alias=True)

    id: str | None = ninja.Field(default=None, alias="_id")
    data: dict
    # _fvid: int # ???

    @staticmethod
    def from_model(model: FormioSubmission):
        return SubmissionResponse(_id=str(model.id), data=model.data)


@router.get("/{name}", auth=require_login)
def get_formio_form(request, name: str):
    task = get_task(request, name)
    return get_form_for_task(task)


@router.post("/{name}/submission", auth=require_login)
def submit_formio_form(request, name: str, body: CreateSubmissionRequest) -> SubmissionResponse:
    task = get_task(request, name)
    assert not task.formio_submission
    submission = FormioSubmission.objects.create(
        task=task,
        data=body.data,
        metadata=body.metadata,
        submitted_at=None if body.state == "draft" else timezone.now(),
    )
    if submission.submitted_at:
        logger.info("Marking task as completed", extra={"task_id": task.id})
        complete_task(task)
    return SubmissionResponse(_id=str(submission.id), data=submission.data)


@router.get("/{name}/submission", auth=require_login)
def list_formio_form_submissions(request, name: str, state: SubmissionState | None = None) -> list[SubmissionResponse]:
    task = get_task(request, name)
    submission = task.formio_submission
    if submission and (state is None or submission.state == state):
        return [SubmissionResponse.from_model(submission)]
    return []


@router.get("/{name}/submission/{submission_id}", auth=require_login)
def get_formio_form_submission(request, name: str, submission_id: str) -> SubmissionResponse:
    task = get_task(request, name)
    submission = get_submission(task, submission_id)
    return SubmissionResponse.from_model(submission)


# TODO-NG: what decides which of the following routes is used?
@router.put("/{name}/submission", auth=require_login)
def update_formio_form_submission_without_id(request, name: str, body: UpdateSubmissionRequest) -> SubmissionResponse:
    task = get_task(request, name)
    submission = get_submission(task, body.id)
    return _update_submission(submission, body)


@router.put("/{name}/submission/{submission_id}", auth=require_login)
def update_formio_form_submission_with_id(
    request, name: str, submission_id: str, body: UpdateSubmissionRequest
) -> SubmissionResponse:
    assert body.id == submission_id
    task = get_task(request, name)
    submission = get_submission(task, submission_id)
    return _update_submission(submission, body)


def _update_submission(submission: FormioSubmission, body: UpdateSubmissionRequest) -> SubmissionResponse:
    assert submission.state == "draft"
    submission.data = body.data
    if body.state == "submitted":
        submission.submitted_at = timezone.now()
    if body.metadata:
        submission.metadata = body.metadata
    submission.save()

    if submission.submitted_at:
        logger.info("Marking task as completed", extra={"task_id": submission.task.id})
        complete_task(submission.task)

    return SubmissionResponse.from_model(submission)
