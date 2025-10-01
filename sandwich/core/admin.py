from django.contrib import admin

from sandwich.core.models import Encounter
from sandwich.core.models import Invitation
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Task
from sandwich.core.models import Template

admin.site.register(
    [Encounter, Invitation, Organization, Patient, Task, Template],
)
