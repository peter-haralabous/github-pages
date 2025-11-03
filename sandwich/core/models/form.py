import pghistory
from django.db import models

from sandwich.core.mixins.versioning import VersionMixin
from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.organization import Organization


class FormManager(models.Manager["Form"]):
    def create(self, **kwargs) -> "Form":
        from sandwich.core.service.form_service import assign_default_form_permissions  # noqa: PLC0415

        form = super().create(**kwargs)
        assign_default_form_permissions(form)
        return form


@pghistory.track()
class Form(VersionMixin, BaseModel):
    """A form that can be rendered using the surveyjs library."""

    name = models.CharField(max_length=255, help_text="The name of the form")
    schema = models.JSONField(
        default=dict,
        help_text="The surveyjs JSON schema of the form",
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    objects = FormManager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_form_name_per_organization")
        ]

    def current_version(self) -> int:
        return self.get_total_versions()
