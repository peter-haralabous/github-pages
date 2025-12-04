from abc import ABC
from abc import abstractmethod
from argparse import ArgumentParser
from argparse import _SubParsersAction
from collections.abc import Callable
from collections.abc import Sequence
from typing import Any
from typing import Protocol

from django.core.management.base import CommandParser

from sandwich.core.management.lib.base import BaseCommandProtocol

type PositionalArgs = tuple[Any, ...]
type KeywordArgs = dict[str, Any]
type Args = tuple[PositionalArgs, KeywordArgs]


class SubcommandMixinProtocol(Protocol):
    """Mixin protocol for SubcommandMixin subclasses"""

    noun: str
    help: str

    def add_subcommand(
        self,
        verb: str,
        func: Callable[..., Any],
        arguments: Sequence[Args] | None = None,
        **kwargs: Any,
    ) -> ArgumentParser: ...


class SelfProtocol(
    SubcommandMixinProtocol,
    BaseCommandProtocol,
    Protocol,
):
    """Private protocol for ListSubcommandMixin"""


class SubcommandMixin(ABC):
    """A mixin to support adding subcommands to django management commands

    ! Intended for use with BaseCommand
    """

    @property
    @abstractmethod
    def noun(self) -> str:
        raise NotImplementedError

    _subparsers: "_SubParsersAction[CommandParser]"

    @property
    def help(self) -> str:
        return f"Manage {self.noun}"

    def add_subcommand(
        self,
        verb: str,
        func: Callable[..., Any],
        arguments: Sequence[Args] | None = None,
        **kwargs: Any,
    ) -> ArgumentParser:
        """Add a subcommand to the command parser."""
        subcommand_parser = self._subparsers.add_parser(verb, **kwargs)
        if arguments:
            for args, arg_kwargs in arguments:
                subcommand_parser.add_argument(*args, **arg_kwargs)
        subcommand_parser.set_defaults(subcommand=func)
        return subcommand_parser

    def add_arguments(self, parser: CommandParser) -> None:
        self._subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)
        super().add_arguments(parser)  # type: ignore[misc]

    def handle(
        self,
        *args: Any,
        subcommand: Callable[..., Any],
        **options: Any,
    ) -> None:
        """Handle the command by calling the specified subcommand."""
        subcommand(**options)
