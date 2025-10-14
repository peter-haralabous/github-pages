from django.urls import path

from .api import api
from .views.consent import patient_consent
from .views.document import delete
from .views.document import upload
from .views.home import home
from .views.invitation import accept_invite
from .views.patient import patient_add
from .views.patient import patient_details
from .views.patient import patient_edit
from .views.patient import patient_onboarding_add
from .views.task import task

app_name = "patients"
urlpatterns = [
    path("", home, name="home"),
    path("consent/", patient_consent, name="consent"),
    path("patient/add", patient_add, name="patient_add"),
    path("patient/onboarding/add", patient_onboarding_add, name="patient_onboarding_add"),
    path("patient/<uuid:patient_id>", patient_details, name="patient_details"),
    path("patient/<uuid:patient_id>/edit", patient_edit, name="patient_edit"),
    path("invite/<str:token>/accept", accept_invite, name="accept_invite"),
    path("patient/<uuid:patient_id>/task/<uuid:task_id>", task, name="task"),
    path("patient/<uuid:patient_id>/document/upload", upload, name="document_upload"),
    path("patient/<uuid:patient_id>/document/<uuid:document_id>/delete/", delete, name="document_delete"),
    path("api/", api.urls, name="api"),
]
