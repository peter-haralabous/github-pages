import pathlib
from typing import Any

from django.core.management import CommandParser

from sandwich.core.management.lib.logging import LoggingCommandProtocol
from sandwich.core.management.lib.logging import LoggingMixin


class StorageMixin(LoggingMixin):
    storage_default: pathlib.Path

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--storage", default=self.storage_default, type=pathlib.Path)
        super().add_arguments(parser)  # type: ignore[misc]

    def handle(self: LoggingCommandProtocol, *args: Any, **options: Any) -> Any:
        self.configure(**options)
        storage = options["storage"]
        if not storage.exists():
            self.info(f"Creating {storage}")
            storage.mkdir(mode=0o777, parents=True, exist_ok=True)
        return super().handle(*args, **options)  # type: ignore[safe-super]
