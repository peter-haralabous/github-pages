from typing import Literal

from django.db import models

from sandwich.core.models.abstract import TimestampedModel


class FormioSubmission(TimestampedModel):
    task = models.OneToOneField("Task", on_delete=models.CASCADE, related_name="_formio_submission")

    data = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)

    submitted_at = models.DateTimeField(null=True)

    @property
    def state(self) -> Literal["submitted", "draft"]:
        return "submitted" if self.submitted_at else "draft"
