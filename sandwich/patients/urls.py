from django.urls import path

from .api import api
from .views.chat import chat
from .views.consent import patient_consent
from .views.document import document_delete
from .views.document import document_download
from .views.document import document_upload_and_extract
from .views.home import home
from .views.invitation import accept_invite
from .views.patient.add import patient_add
from .views.patient.add import patient_onboarding_add
from .views.patient.details import fact_edit
from .views.patient.details import patient_details
from .views.patient.edit import get_phn_validation
from .views.patient.edit import patient_edit
from .views.patient.health_records import condition_edit
from .views.patient.health_records import document_edit
from .views.patient.health_records import health_records_add
from .views.patient.health_records import immunization_edit
from .views.patient.health_records import patient_records
from .views.patient.health_records import patient_repository
from .views.patient.health_records import patient_tasks
from .views.patient.health_records import practitioner_edit
from .views.task import task

app_name = "patients"
urlpatterns = [
    path("", home, name="home"),
    path("chat/", chat, name="chat"),
    path("consent/", patient_consent, name="consent"),
    path("patient/add", patient_add, name="patient_add"),
    path("patient/onboarding/add", patient_onboarding_add, name="patient_onboarding_add"),
    path("patient/<uuid:patient_id>", patient_details, name="patient_details"),
    path("patient/<uuid:patient_id>/edit", patient_edit, name="patient_edit"),
    path("patient/<uuid:patient_id>/records", patient_records, name="patient_records"),
    path("patient/<uuid:patient_id>/records/<str:record_type>", patient_records, name="patient_records"),
    path("patient/<uuid:patient_id>/repository", patient_repository, name="patient_repository"),
    path("patient/<uuid:patient_id>/repository/<str:category>", patient_repository, name="patient_repository"),
    path("patient/<uuid:patient_id>/tasks", patient_tasks, name="patient_tasks"),
    path(
        "patient/<uuid:patient_id>/health_records/<str:record_type>/add", health_records_add, name="health_records_add"
    ),
    path("invite/<str:token>/accept", accept_invite, name="accept_invite"),
    path("patient/<uuid:patient_id>/task/<uuid:task_id>", task, name="task"),
    path("patient/<uuid:patient_id>/document/upload", document_upload_and_extract, name="document_upload_and_extract"),
    path("patient/<uuid:patient_id>/document/<uuid:document_id>/delete/", document_delete, name="document_delete"),
    path("condition/<uuid:condition_id>", condition_edit, name="condition"),
    path("document/<uuid:document_id>", document_edit, name="document"),
    path("document/<uuid:document_id>/download", document_download, name="document_download"),
    path("immunization/<uuid:immunization_id>", immunization_edit, name="immunization"),
    path("practitioner/<uuid:practitioner_id>", practitioner_edit, name="practitioner"),
    path("api/", api.urls, name="api"),
    path("get_phn_validation/", get_phn_validation, name="get_phn_validation"),
    path("fact/<uuid:fact_id>/edit", fact_edit, name="fact_edit"),
]
