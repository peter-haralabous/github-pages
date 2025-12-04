from typing import Any

from django.conf import settings
from django.core.management import CommandParser

from sandwich.core.factories.template import TemplateFactory
from sandwich.core.management.lib.generic import CreateListDeleteCommand
from sandwich.core.management.lib.json import json_object_type
from sandwich.core.management.types import template_type
from sandwich.core.models import Template
from sandwich.core.models.email import EmailType
from sandwich.core.service.email_service import send_email
from sandwich.core.service.template_service import render_template


class Command(CreateListDeleteCommand[Template]):
    model = Template
    factory = TemplateFactory

    @staticmethod
    def arg_type(value: Any) -> Template:
        return template_type(value)

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)  # type: ignore[misc]
        self.add_subcommand(
            "render",
            self.render,
            arguments=[
                (("template",), {"type": self.arg_type}),
                (("--email",), {"default": None, "help": "Send output as email to this address"}),
                (
                    ("--context",),
                    {"type": json_object_type, "default": None, "help": "JSON context for rendering the template"},
                ),
                (
                    ("--language",),
                    {"default": settings.LANGUAGE_CODE, "help": "The language of the template to render"},
                ),
            ],
        )

    def render(self, template: Template, context: dict[str, Any] | None, email: str | None, language: str, **_) -> str:
        """
        Example invocation:

        ./manage.py template render email/welcome \
            --email test@test.ca \
            --context '{ \
                "app_url": "https://hc.wethrive.ninja", \
                "cta_link": "https://www.thrive.health/", \
                "cta_text": "CLICK ME"\
                }' \
            --language fr-ca
        """

        if context is None:
            context = {}
        rendered_template = render_template(template, context=context, language=language)
        if email:
            send_email(
                to=email,
                subject=f"Rendered Template: {template.slug}",
                body=rendered_template,
                email_type=EmailType.invitation,
            )
        else:
            self.output(rendered_template)
        return rendered_template
