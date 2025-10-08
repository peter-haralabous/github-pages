import logging

from csp.constants import NONCE
from csp.decorators import csp_update
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.task import terminal_task_status
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


# formio is here being loaded by CDN, which would cut down on requiring us to add the script/style/font src
# but that unsafe-eval seems to be a core function of how formio works
@csp_update(
    {
        "script-src-elem": (NONCE, "https://cdn.form.io/js/formio.form.js"),
        "script-src": "'unsafe-eval'",
        # Allow required external stylesheets.
        "style-src-elem": (
            "https://cdn.form.io/js/formio.form.min.css",
            "https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css",
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css",
        ),
        # Allow required icon fonts (exact font file paths). Using explicit paths keeps scope narrow.
        "font-src": (
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff2",
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff",
        ),
    }
)
@csp_update(  # type: ignore[arg-type]
    {
        "script-src-elem": (NONCE, "https://cdn.form.io/js/formio.form.js"),
        "script-src": "'unsafe-eval'",
        "style-src-elem": (
            "https://cdn.form.io/js/formio.form.min.css",
            "https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css",
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css",
        ),
        "font-src": (
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff2",
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff",
        ),
    },
    REPORT_ONLY=True,
)
@login_required
def task(request: AuthenticatedHttpRequest, patient_id: int, task_id: int) -> HttpResponse:
    logger.info(
        "Accessing patient task", extra={"user_id": request.user.id, "patient_id": patient_id, "task_id": task_id}
    )

    patient = get_object_or_404(request.user.patient_set, id=patient_id)
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
        "patient/form.html",
        context={"form_url": form_url, "formio_user": formio_user, "read_only": read_only},
    )
