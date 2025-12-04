from argparse import ArgumentParser
from collections.abc import Collection
from collections.abc import Iterable
from functools import cache
from typing import Any
from typing import Protocol
from typing import TypedDict

import tablib
from django.db.models import Model
from django.db.models import QuerySet
from tablib.formats import registry

from sandwich.core.management.lib.base import BaseCommandProtocol


@cache
def _valid_tablib_format() -> list[str]:
    return list(registry._formats.keys())  # noqa: SLF001


class ReportDict(TypedDict):
    headers: Collection[str]
    data: Collection[Collection[str | None]]


class ReportMixinProtocol[M: Model](Protocol):
    """Mixin protocol for ReportMixin subclasses"""

    default_sort: str

    def add_report_arguments(self, parser: ArgumentParser) -> None: ...

    def report(self, headers: Iterable[str], data: Iterable[Iterable[Any]], **options: Any) -> None: ...

    def queryset_report(
        self,
        qs: QuerySet[M],
        headers: None | Iterable[str] = None,
        **options: Any,
    ) -> None: ...


class SelfProtocol(
    ReportMixinProtocol,
    BaseCommandProtocol,
    Protocol,
):
    """Private protocol for ReportMixin"""


class ReportMixin:
    """A mixin to support outputting structured data as a report using tablib and stdout

    ! Intended for use with BaseCommand
    """

    default_sort: str | None = None

    def add_report_arguments(self: SelfProtocol, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--format",
            dest="format_",
            default=None,
            choices=_valid_tablib_format(),
        )
        parser.add_argument("--sort", default=self.default_sort)

    def queryset_report(
        self: SelfProtocol,
        qs: QuerySet[Model],
        headers: None | Iterable[str] = None,
        **options: Any,
    ) -> None:
        if not qs:
            self.stderr.write("No data found")
            return
        if headers is None:
            fields = qs[0].__class__._meta.get_fields()  # noqa: SLF001
            headers = [f.name for f in filter(lambda f: not f.is_relation, fields)]
        self.report(
            headers=headers,
            data=[[getattr(obj, field) for field in headers] for obj in qs],
            **options,
        )

    def report(
        self: SelfProtocol,
        headers: Iterable[str],
        data: Iterable[Iterable[Any]],
        cli_prefix: str | None = None,
        cli_suffix: str | None = None,
        format_: str | None = None,
        **options: Any,
    ) -> None:
        """Write the report to stdout

        To provide additional information on the cli output only, pass cli_prefix and/or cli_suffix
        """
        dataset = tablib.Dataset(*data, headers=headers)
        prefix = None
        suffix = None
        if format_ and format_ != "cli":
            kwargs = {"format": format_}
        else:
            kwargs = {"format": "cli", "tablefmt": "github"}
            prefix = cli_prefix
            suffix = cli_suffix

        if options.get("sort", False):
            dataset = dataset.sort(options["sort"])

        if prefix:
            self.stdout.write(prefix)
        self.stdout.write(dataset.export(**kwargs))
        if suffix:
            self.stdout.write(suffix)
