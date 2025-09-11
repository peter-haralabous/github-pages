from django.urls import path

from .views.home import home
from .views.patient import patient_add
from .views.patient import patient_details
from .views.patient import patient_edit

app_name = "patients"
urlpatterns = [
    path("", home, name="home"),
    path("patient/add", patient_add, name="patient_add"),
    path("patient/<int:patient_id>", patient_details, name="patient_details"),
    path("patient/<int:patient_id>/edit", patient_edit, name="patient_edit"),
]
