from django.db import models

from sandwich.core.models import Organization
from sandwich.core.models.abstract import BaseModel


class TemplateManager(models.Manager["Template"]):
    """
    Manager to support natural keys

    https://docs.djangoproject.com/en/stable/topics/serialization/#natural-keys
    """

    def get_by_natural_key(self, slug: str, organization_slug: str | None) -> "Template":
        if organization_slug:
            return self.get(slug=slug, organization=Organization.objects.get_by_natural_key(organization_slug))
        return self.get(slug=slug, organization__isnull=True)


class Template(BaseModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE, blank=True, null=True)
    slug = models.CharField(
        max_length=255, help_text="The unique identifier for this template within the organization."
    )
    description = models.TextField(blank=True, help_text="A brief description of the template's purpose.")
    content = models.TextField(help_text="Markdown formatted content with optional django templating.")

    objects = TemplateManager()  # type: ignore[django-manager-missing]

    class Meta:
        unique_together = ("organization", "slug")
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.slug}:{self.organization_id}"

    def natural_key(self) -> tuple[object, ...]:
        if self.organization:
            return self.slug, *self.organization.natural_key()
        return self.slug, None

    natural_key.dependencies = ["core.organization"]  # type: ignore[attr-defined]
