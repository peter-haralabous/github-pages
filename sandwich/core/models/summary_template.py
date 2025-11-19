from django.db import models

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.organization import Organization
from sandwich.core.service.summary_template_service import assign_default_summarytemplate_permissions


class SummaryTemplateManager(models.Manager["SummaryTemplate"]):
    def create(self, **kwargs) -> "SummaryTemplate":
        summary_template = super().create(**kwargs)
        assign_default_summarytemplate_permissions(summary_template)
        return summary_template


class SummaryTemplate(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, help_text="Organization that owns this template"
    )

    name = models.CharField(max_length=255, help_text="Display name for the template")

    description = models.TextField(blank=True, help_text="Optional description of the template's purpose and usage")

    text = models.TextField(help_text="Template content using Django template syntax with {% ai %} tags")

    form = models.ForeignKey(
        "Form",
        on_delete=models.CASCADE,
        help_text="Form that this template is associated with",
    )

    objects = SummaryTemplateManager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_template_name_per_organization")
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.organization.slug})"
