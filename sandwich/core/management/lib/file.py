import base64
from argparse import ArgumentError
from argparse import ArgumentParser
from pathlib import Path
from typing import Any
from typing import Protocol

from django.core.management.base import CommandParser

from sandwich.core.management.lib.base import BaseCommandProtocol


class FileIOMixinProtocol(Protocol):
    def add_input_arguments(self, parser: CommandParser) -> None: ...
    def add_output_arguments(self, parser: CommandParser) -> None: ...
    def read_input(self, text: str | None, input_: Path | None, **_: dict[str, Any]) -> str: ...
    def write_output(self, content: str, output: Path | None, **_: dict[str, Any]) -> None: ...


class SelfProtocol(
    FileIOMixinProtocol,
    BaseCommandProtocol,
    Protocol,
):
    pass


class FileIOMixin:
    def add_input_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--text", dest="input_text", default=None)
        parser.add_argument("--input", dest="input_path", type=Path, default=None)

    def add_output_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--output", dest="output_path", type=Path, default=None)

    def read_input_bytes(
        self,
        input_text: str | None,
        input_path: Path | None,
        **_: dict[str, Any],
    ) -> bytes:
        if not bool(input_text) ^ bool(input_path):
            raise ArgumentError(None, "You must provide either --text or --input.")
        return input_path.read_bytes() if input_path else base64.b64decode(input_text)  # type: ignore[arg-type]

    def read_input_text(
        self,
        input_text: str | None,
        input_path: Path | None,
        **_: dict[str, Any],
    ) -> str:
        if not bool(input_text) ^ bool(input_path):
            raise ArgumentError(None, "You must provide either --text or --input.")
        return input_path.read_text() if input_path else input_text  # type: ignore[return-value]

    def write_output_bytes(
        self: SelfProtocol,
        content: bytes,
        output_path: Path | None,
        **_: dict[str, Any],
    ) -> None:
        if output_path:
            output_path.write_bytes(content)
        else:
            self.stdout.write(str(base64.b64encode(content)))

    def write_output_text(
        self: SelfProtocol,
        content: str,
        output_path: Path | None,
        **_: dict[str, Any],
    ) -> None:
        if output_path:
            output_path.write_text(content)
        else:
            self.stdout.write(content)
