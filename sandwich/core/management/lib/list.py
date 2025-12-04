from argparse import ArgumentParser
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any
from typing import Protocol

from django.core.management.base import CommandParser
from django.db.models import Model

from sandwich.core.management.lib.model import ModelReportMixinProtocol
from sandwich.core.management.lib.report import ReportMixinProtocol
from sandwich.core.management.lib.subcommand import Args
from sandwich.core.management.lib.subcommand import SubcommandMixinProtocol


class ListSubcommandMixinProtocol[M: Model](Protocol):
    """Mixin protocol for ListSubcommandMixin subclasses"""

    def add_list_arguments(self) -> ArgumentParser: ...
    def list_arguments(self) -> Sequence[Args]: ...
    def list_(self: SubcommandMixinProtocol, **kwargs: Any) -> Iterable[M]: ...
    def list_filter(self, **kwargs: Any) -> dict[str, Any]: ...
    def list_output(self, objs: Iterable[M], **kwargs: Any) -> None: ...


class SelfProtocol[M: Model](
    ListSubcommandMixinProtocol,
    ModelReportMixinProtocol,
    SubcommandMixinProtocol,
    ReportMixinProtocol,
    Protocol,
):
    """Private protocol for ListSubcommandMixin"""


class ListSubcommandMixin[M: Model]:
    """A mixin to support listing model instances as a subcommand of a django management command

    ! Intended for use with: ModelReportMixin, SubcommandMixin, ReportMixin and BaseCommand
    """

    def add_arguments(self: SelfProtocol[M], parser: CommandParser) -> None:
        super().add_arguments(parser)  # type: ignore[misc]
        self.add_list_arguments()

    def add_list_arguments(self: SelfProtocol[M]) -> ArgumentParser:
        list_ = self.add_subcommand("list", self.list_, self.list_arguments(), aliases=["l"])
        self.add_report_arguments(list_)
        return list_

    def list_arguments(self: SelfProtocol[M]) -> list[Args]:
        return []

    def list_(
        self: SelfProtocol[M],
        **kwargs: Any,
    ) -> Iterable[M]:
        objects = self.model._default_manager.filter(**self.list_filter(**kwargs))  # noqa: SLF001
        self.list_output(objects, **kwargs)
        return objects

    def list_filter(self: SelfProtocol[M], **kwargs: Any) -> dict[str, Any]:
        return {}

    def list_output(self: SelfProtocol[M], objects: Iterable[M], **kwargs: Any) -> None:
        """Output the list of objects."""
        self.model_report(objects, **kwargs)
