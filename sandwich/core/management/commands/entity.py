from django.conf import settings
from django.core.management import BaseCommand
from django.core.management import CommandParser
from django.core.management import call_command

from sandwich.core.management.lib.logging import LoggingMixin
from sandwich.core.management.lib.subcommand import SubcommandMixin
from sandwich.core.models import Entity
from sandwich.core.models.entity import EntityType


def primary_keys(entity_type: EntityType, **_) -> list[str]:
    return [str(e) for e in Entity.objects.filter(type=entity_type.value).order_by("id").values_list("id", flat=True)]


class Command(SubcommandMixin, LoggingMixin, BaseCommand):  # type: ignore[override]
    noun = "Entity"

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        self.add_subcommand(
            "save-fixtures",
            self.save_fixtures,
        )

    def save_fixtures(self, *args, **kwargs) -> None:
        for entity_type in EntityType:
            output_path = f"{settings.APPS_DIR}/core/fixtures/entity_{entity_type.value.lower()}.json"

            if pks := ",".join(primary_keys(entity_type)):
                self.info(f"Saving {entity_type.value} entities to {output_path}")
                call_command(
                    "dumpdata",
                    "core.entity",
                    primary_keys=pks,
                    use_natural_primary_keys=True,
                    use_natural_foreign_keys=True,
                    indent=2,
                    output=output_path,
                    format="sandwich",
                )
            else:
                self.info(f"Skipping {entity_type.value} entities")
