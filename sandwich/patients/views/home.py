from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from sandwich.core.models import Patient
from sandwich.users.models import User


@login_required
def home(request: HttpRequest) -> HttpResponse:
    assert isinstance(request.user, User)
    patient = Patient.objects.filter(user=request.user).first()
    if patient:
        return redirect("patients:patient", pk=patient.id)

    return render(request, "patient/home.html")
