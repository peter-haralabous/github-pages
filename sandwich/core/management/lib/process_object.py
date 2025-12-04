import json
from argparse import ArgumentError
from argparse import ArgumentParser
from textwrap import dedent
from typing import Any
from typing import Literal
from typing import Protocol

from sandwich.core.service.aws.common import ProcessResult
from sandwich.core.service.aws.common import ProcessType

ProcessFormat = Literal["markdown", "json", "mixed"]


class ProcessObjectMixinProtocol(Protocol):
    def process_output(
        self,
        results: list[ProcessResult],
        process_format: ProcessFormat = "mixed",
    ) -> str: ...


class ProcessObjectMixin:
    def add_process_arguments(self, parser: ArgumentParser, default: ProcessFormat | None = None) -> None:
        parser.add_argument(
            "--format",
            choices=["mixed", "json", "markdown"],
            default=default if default else "mixed",
            dest="process_format",
        )

    @staticmethod
    def _section(result: ProcessResult) -> str:
        return dedent(f"""
            The following {result.destination.type} was generated from the {result.source.type}:
            ---
            """)

    def process_output(
        self,
        results: list[ProcessResult],
        process_format: ProcessFormat = "mixed",
        **_: dict[str, Any],
    ) -> str:
        output = ""
        match process_format:
            case "markdown":
                for result in filter(lambda r: r.destination.type == ProcessType.MARKDOWN, results):
                    output += self._section(result)
                    output += result.destination.str
            case "json":
                output = json.dumps(
                    {
                        result.destination.type: json.loads(result.destination.str)
                        for result in filter(
                            lambda r: r.destination.type != ProcessType.MARKDOWN,
                            results,
                        )
                    },
                    indent=2,
                )
            case "mixed":
                for result in results:
                    output += self._section(result)
                    match result.destination.type:
                        case ProcessType.MARKDOWN:
                            output += result.destination.str
                        case _:
                            output += "\n```json\n"
                            output += json.dumps(json.loads(result.destination.str), indent=2)
                            output += "\n```\n"
            case _:
                raise ArgumentError(None, f"Unknown format: {process_format}")

        return output
