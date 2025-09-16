from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.task import TaskStatus
from sandwich.core.models.task import terminal_task_status
from sandwich.core.util.http import AuthenticatedHttpRequest


@login_required
def task(request: AuthenticatedHttpRequest, patient_id: int, task_id: int) -> HttpResponse:
    patient = get_object_or_404(request.user.patient_set, id=patient_id)
    task = get_object_or_404(patient.task_set, id=task_id)

    # NOTE-NG: we're using the task ID here as the form name
    # patients don't have permission to load arbitrary forms
    read_only = terminal_task_status(cast("TaskStatus", task.status))
    # no, I don't want to catch RelatedObjectDoesNotExist if there's no submission yet
    if task.formio_submission:
        form_url = request.build_absolute_uri(
            reverse(
                "patients:api-1.0.0:get_formio_form_submission",
                kwargs={"name": str(task_id), "submission_id": str(task.formio_submission.id)},
            )
        )
    else:
        form_url = request.build_absolute_uri(
            reverse("patients:api-1.0.0:get_formio_form", kwargs={"name": str(task_id)})
        )
    formio_user = {"_id": request.user.id}

    return render(
        request,
        "patient/form.html",
        context={"form_url": form_url, "formio_user": formio_user, "read_only": read_only},
    )
