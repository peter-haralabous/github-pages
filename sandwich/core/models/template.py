from django.db import models

from sandwich.core.models.abstract import BaseModel


class Template(BaseModel):  # type: ignore[django-manager-missing] # see docs/typing
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE, blank=True, null=True)
    slug = models.CharField(
        max_length=255, help_text="The unique identifier for this template within the organization."
    )
    description = models.TextField(blank=True, help_text="A brief description of the template's purpose.")
    content = models.TextField(help_text="Markdown formatted content with optional django templating.")

    class Meta:
        unique_together = ("organization", "slug")
        ordering = ("created_at",)

    def __str__(self) -> str:
        return self.slug
