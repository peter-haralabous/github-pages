from abc import ABC
from abc import abstractmethod
from argparse import ArgumentParser
from collections.abc import Callable
from typing import Any
from typing import Protocol

from django.core.management.base import CommandParser
from django.db.models import Model

from sandwich.core.management.lib.input import InputMixinProtocol
from sandwich.core.management.lib.logging import LoggingCommandProtocol
from sandwich.core.management.lib.subcommand import SubcommandMixinProtocol


class DeleteSubcommandMixinProtocol[M: Model](Protocol):
    """
    Protocol for commands that have a delete subcommand.

    ! Intended for use with InputMixin, LoggingMixin, SubCommandMixin and BaseCommand
    """

    arg_type: Callable[[str], M]

    def add_delete_arguments(self) -> ArgumentParser: ...
    def delete(self: SubcommandMixinProtocol, **kwargs: Any) -> None: ...


class SelfProtocol[M: Model](
    DeleteSubcommandMixinProtocol,
    SubcommandMixinProtocol,
    InputMixinProtocol,
    LoggingCommandProtocol,
    Protocol,
):
    pass


class DeleteSubcommandMixin[M: Model](ABC):
    @staticmethod
    @abstractmethod
    def arg_type(value: str) -> M:
        raise NotImplementedError

    def add_arguments(self: SelfProtocol[M], parser: CommandParser) -> None:
        super().add_arguments(parser)  # type: ignore[safe-super]
        self.add_delete_arguments()

    def add_delete_arguments(self: SelfProtocol[M]) -> ArgumentParser:
        return self.add_subcommand(
            "delete",
            self.delete,
            [
                (("obj",), {"type": self.__class__.arg_type}),
                (
                    ("--force", "-f"),
                    {"action": "store_true", "help": "Force delete without confirmation"},
                ),
            ],
            aliases=["d", "remove", "rm"],
        )

    def delete(
        self: SelfProtocol[M],
        obj: M,
        *,
        force: bool = False,
        **options: Any,
    ) -> None | str:
        obj_pk = str(obj.pk)
        obj_str = f"<{obj.__class__.__name__}> {obj}"

        if force or self.confirm(f"Are you sure you want to delete {obj_str}? (y/n)"):
            obj.delete()
            self.info(f"{obj_str} deleted.")
            return obj_pk
        return None
