from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.form_submission import FormSubmission
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


TERMINAL_TASK_STATUSES = [TaskStatus.CANCELLED, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.ENTERED_IN_ERROR]
ACTIVE_TASK_STATUSES = [s for s in TaskStatus if s not in TERMINAL_TASK_STATUSES]


class TaskManager(models.Manager["Task"]):
    def create(self, **kwargs) -> "Task":
        from sandwich.core.service.task_service import assign_default_task_perms  # noqa: PLC0415

        created = super().create(**kwargs)
        assign_default_task_perms(created)
        return created


# NOTE-NG: this is just a placeholder for now. We'll want to expand this model significantly in the future.
class Task(BaseModel):
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

    status: models.Field[TaskStatus, TaskStatus] = EnumField(TaskStatus)

    # this is Task.executionPeriod.end in FHIR
    ended_at = models.DateTimeField(blank=True, null=True)

    form_version = models.ForeignKey(
        "core.FormEvent",
        on_delete=models.PROTECT,
        related_name="tasks",
        null=True,
        blank=True,
        help_text="The specific version of the form this task uses",
    )

    objects = TaskManager()

    def clean(self):
        if self.encounter and self.patient and self.encounter.patient != self.patient:
            msg = "Encounter and patient do not match."
            raise ValidationError(msg)

    @property
    def name(self) -> str:
        if self.form_version and self.form_version.name:
            return f'Form "{self.form_version.name}"'
        return f"Task {self.id}"

    @property
    def active(self) -> bool:
        return self.status in ACTIVE_TASK_STATUSES

    def get_form_submission(self) -> FormSubmission | None:
        """
        Get related form submission and handle DoesNotExist exception.
        """
        try:
            return self.form_submission
        except FormSubmission.DoesNotExist:
            return None

    @property
    def formio_submission(self) -> FormioSubmission | None:
        # the default behaviour of ReverseOneToOneDescriptor is to raise an exception, but that's annoying
        try:
            return self._formio_submission
        except FormioSubmission.DoesNotExist:
            return None

    def get_absolute_url(self):
        return reverse("patients:task", kwargs={"task_id": self.id, "patient_id": self.patient.id})

    class Meta:
        permissions = (("complete_task", "Can complete a task."),)
