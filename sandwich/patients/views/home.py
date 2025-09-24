import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def home(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Patient accessing home page", extra={"user_id": request.user.id})

    patient = request.user.patient_set.first()
    if patient:
        logger.info("Redirecting to patient details", extra={"user_id": request.user.id, "patient_id": patient.id})
        return redirect("patients:patient_details", patient_id=patient.id)

    logger.info("Rendering patient home page - no existing patient", extra={"user_id": request.user.id})
    return render(request, "patient/home.html")
