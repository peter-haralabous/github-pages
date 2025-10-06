from inspect import isclass
from typing import Any

from django.conf import settings
from django.db.models import Q
from django.template import Engine
from django.template import Origin
from django.template.loaders.base import Loader
from django.utils import translation
from markdown_it import MarkdownIt

from sandwich.core.models import Organization
from sandwich.core.models import Template
from sandwich.core.types import HtmlStr

type ContextDict = dict[str, Any]


class TemplateOrigin(Origin):
    def __init__(self, template: Template, language: str):
        self.template = template
        self.language = language
        super().__init__(name=template.slug)


class ClassLoaderEngine(Engine):
    """An Engine that can load template loaders from classes directly."""

    def find_template_loader(self, loader: Any) -> Loader:
        if isclass(loader) and issubclass(loader, Loader):
            return loader(self)
        return super().find_template_loader(loader)


def build_template_loader(organization: Organization | None, language: str):
    class TemplateLoader(Loader):
        """A template loader that fetches templates from Template objects that belong to a specific organization.

        https://docs.djangoproject.com/en/stable/ref/templates/api/#custom-loaders
        """

        organization: Organization | None
        language: str

        def get_template_sources(self, template_name: str) -> list[Origin]:
            """

            https://docs.djangoproject.com/en/stable/ref/templates/api/#template-origin
            """
            templates = Template.objects.filter(
                Q(organization=organization) | Q(organization__isnull=True), slug=template_name
            ).order_by("organization_id")  # Prefer organization-specific templates to global ones
            return [TemplateOrigin(template=template, language=self.language) for template in templates]

        @staticmethod
        def get_contents(origin: TemplateOrigin) -> str:
            with translation.override(origin.language):
                return origin.template.content

    TemplateLoader.organization = organization
    TemplateLoader.language = language
    return TemplateLoader


def render(
    template_name: str,
    context: dict[str, Any] | None = None,
    organization: Organization | None = None,
    language: str | None = None,
) -> HtmlStr:
    context = context or {}
    language = language or settings.LANGUAGE_CODE

    engine = ClassLoaderEngine(loaders=[build_template_loader(organization, language)])
    markdown_str = engine.render_to_string(template_name=template_name, context=context)
    return MarkdownIt().render(markdown_str)


def render_template(template: Template, **kwargs: Any) -> HtmlStr:
    return render(template_name=template.slug, organization=template.organization, **kwargs)
