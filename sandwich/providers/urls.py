from django.urls import path

from .views.encounter import encounter_details
from .views.encounter import encounter_list
from .views.home import home
from .views.home import organization_home
from .views.organization import organization_add
from .views.organization import organization_edit
from .views.patient import patient_add
from .views.patient import patient_add_task
from .views.patient import patient_archive
from .views.patient import patient_cancel_task
from .views.patient import patient_details
from .views.patient import patient_edit
from .views.patient import patient_list
from .views.patient import patient_resend_invite
from .views.search import search
from .views.task import task

app_name = "providers"
urlpatterns = [
    path("", home, name="home"),
    path("organization/add", organization_add, name="organization_add"),
    path("organization/<uuid:organization_id>", organization_home, name="organization"),
    path("organization/<uuid:organization_id>/edit", organization_edit, name="organization_edit"),
    path("organization/<uuid:organization_id>/search", search, name="search"),
    path("organization/<uuid:organization_id>/encounters", encounter_list, name="encounter_list"),
    path("organization/<uuid:organization_id>/encounter/<uuid:encounter_id>", encounter_details, name="encounter"),
    path("organization/<uuid:organization_id>/patient/<uuid:patient_id>", patient_details, name="patient"),
    path("organization/<uuid:organization_id>/patient/<uuid:patient_id>/edit", patient_edit, name="patient_edit"),
    path(
        "organization/<uuid:organization_id>/patient/<uuid:patient_id>/archive",
        patient_archive,
        name="patient_archive",
    ),
    path(
        "organization/<uuid:organization_id>/patient/<uuid:patient_id>/add_task",
        patient_add_task,
        name="patient_add_task",
    ),
    path(
        "organization/<uuid:organization_id>/patient/<uuid:patient_id>/resend_invite",
        patient_resend_invite,
        name="patient_resend_invite",
    ),
    path("organization/<uuid:organization_id>/patient/<uuid:patient_id>/task/<uuid:task_id>", task, name="task"),
    path(
        "organization/<uuid:organization_id>/patient/<uuid:patient_id>/task/<uuid:task_id>/cancel",
        patient_cancel_task,
        name="patient_cancel_task",
    ),
    path("organization/<uuid:organization_id>/patients", patient_list, name="patient_list"),
    path("organization/<uuid:organization_id>/patient/add", patient_add, name="patient_add"),
]
