from django.contrib import admin

from sandwich.core.models import Condition
from sandwich.core.models import Document
from sandwich.core.models import Encounter
from sandwich.core.models import FormioSubmission
from sandwich.core.models import HealthSummary
from sandwich.core.models import Immunization
from sandwich.core.models import Invitation
from sandwich.core.models import Practitioner
from sandwich.core.models import Task

# For some reason ruff wants a redundant alias
from .consent import ConsentAdmin as ConsentAdmin
from .email import EmailAdmin as EmailAdmin
from .entity import EntityAdmin as EntityAdmin
from .fact import FactAdmin as FactAdmin
from .list_preference import ListViewPreferenceAdmin as ListViewPreferenceAdmin
from .organization import OrganizationAdmin as OrganizationAdmin
from .patient import PatientAdmin as PatientAdmin
from .predicate import PredicateAdmin as PredicateAdmin
from .template import TemplateAdmin as TemplateAdmin

admin.site.register(
    [
        Condition,
        Document,
        Encounter,
        FormioSubmission,
        HealthSummary,
        Immunization,
        Invitation,
        Practitioner,
        Task,
    ],
)
