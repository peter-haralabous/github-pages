from typing import Any
from typing import Protocol

from django.core.management import CommandParser
from django.core.management.base import OutputWrapper


class BaseCommandProtocol(Protocol):
    stdout: OutputWrapper
    stderr: OutputWrapper

    def add_arguments(self, parser: CommandParser) -> None: ...

    def handle(self, *args: Any, **kwargs: Any) -> None: ...
