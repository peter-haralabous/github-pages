from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from sandwich.core.util.http import AuthenticatedHttpRequest


@login_required
def home(request: AuthenticatedHttpRequest) -> HttpResponse:
    patient = request.user.patient_set.first()
    if patient:
        return redirect("patients:patient_details", patient_id=patient.id)

    return render(request, "patient/home.html")
