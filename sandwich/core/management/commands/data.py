from django.core.management import BaseCommand
from django.core.management import CommandParser

from sandwich.core.management.lib.subcommand import SubcommandMixin
from sandwich.users.models import User


class Command(SubcommandMixin, BaseCommand):  # type: ignore[override]
    noun = "Data"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        self.add_subcommand(
            "generate",
            self.generate,
            arguments=[],
        )

    def generate(self, **_) -> None:
        User.objects.create_superuser(email="admin@admin.admin", password="admin")  # noqa: S106
