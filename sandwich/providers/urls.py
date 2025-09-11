from django.urls import path

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

app_name = "providers"
urlpatterns = [
    path("", home, name="home"),
    path("organization/add", organization_add, name="organization_add"),
    path("organization/<int:organization_id>/patient/<int:patient_id>", patient_details, name="patient"),
    path("organization/<int:organization_id>/patient/<int:patient_id>/edit", patient_edit, name="patient_edit"),
    path(
        "organization/<int:organization_id>/patient/<int:patient_id>/archive", patient_archive, name="patient_archive"
    ),
    path(
        "organization/<int:organization_id>/patient/<int:patient_id>/add_task",
        patient_add_task,
        name="patient_add_task",
    ),
    path(
        "organization/<int:organization_id>/patient/<int:patient_id>/task/<int:task_id>/cancel",
        patient_cancel_task,
        name="patient_cancel_task",
    ),
    path("organization/<int:organization_id>/patients", patient_list, name="patient_list"),
    path("organization/<int:organization_id>/patient/add", patient_add, name="patient_add"),
    path("organization/<int:organization_id>", organization_home, name="organization"),
    path("organization/<int:organization_id>/edit", organization_edit, name="organization_edit"),
]
