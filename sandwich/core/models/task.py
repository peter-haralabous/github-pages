from django.db import models
from django.utils.translation import gettext_lazy as _

from sandwich.core.models import Encounter
from sandwich.core.models.abstract import TimestampedModel
from sandwich.core.models.formio_submission import FormioSubmission
from sandwich.core.models.patient import Patient


class TaskStatus(models.TextChoices):
    """
    https://hl7.org/fhir/R5/valueset-task-status.html
    """

    # These are more options than we want to expose in the UI, but we'll want at least a couple.
    # Don't add new ones! This comes from the FHIR spec.
    DRAFT = "draft", _("Draft")
    REQUESTED = "requested", _("Requested")
    RECEIVED = "received", _("Received")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")
    READY = "ready", _("Ready")
    CANCELLED = "cancelled", _("Cancelled")
    IN_PROGRESS = "in-progress", _("In Progress")
    ON_HOLD = "on-hold", _("On Hold")
    FAILED = "failed", _("Failed")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


def terminal_task_status(status: TaskStatus) -> bool:
    return status in [TaskStatus.CANCELLED, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.ENTERED_IN_ERROR]


# NOTE-NG: this is just a placeholder for now. We'll want to expand this model significantly in the future.
class Task(TimestampedModel):
    """
    A task to be performed.

    https://hl7.org/fhir/R5/task.html
    """

    # we may want to add to better support sharding or access control,
    # but it's also available as both .encounter.organization and .patient.organization
    # organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    # this is Task.for in FHIR
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE)

    status = models.CharField(max_length=255, choices=TaskStatus)

    # this is Task.executionPeriod.end in FHIR
    ended_at = models.DateTimeField(blank=True, null=True)

    @property
    def name(self) -> str:
        return f"Task {self.id}"

    @property
    def active(self) -> bool:
        # FIXME-NG: self.status is a str, not a TaskStatus
        return not terminal_task_status(self.status)  # type: ignore[arg-type]

    @property
    def formio_submission(self) -> FormioSubmission | None:
        # the default behaviour of ReverseOneToOneDescriptor is to raise an exception, but that's annoying
        try:
            return self._formio_submission
        except FormioSubmission.DoesNotExist:
            return None
