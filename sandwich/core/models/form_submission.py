from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task
from sandwich.users.models import User


class FormSubmissionStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    COMPLETED = "completed", _("Completed")


class FormSubmission(BaseModel):
    """
    Stores a patient's data for a specific form, linking it to an assigned task.
    """

    task = models.OneToOneField(
        Task, on_delete=models.SET_NULL, null=True, blank=True, help_text="The specific task this submission is for"
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, help_text="The patient this form submission is for")
    status: models.Field[FormSubmissionStatus, FormSubmissionStatus] = EnumField(
        FormSubmissionStatus, help_text="current state of submission"
    )
    form_version = models.ForeignKey(
        "core.FormEvent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The specific version of the form this submission uses",
    )
    data = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)

    submitted_at = models.DateTimeField(null=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, help_text="The user who filled out the submission"
    )

    def submit(self, user):
        if self.status == FormSubmissionStatus.DRAFT:
            self.status = FormSubmissionStatus.COMPLETED
            self.submitted_by = user
            self.submitted_at = timezone.now()
            self.save()
