from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any
from typing import Protocol

from django.db.models import Model

from sandwich.core.management.lib.report import ReportMixinProtocol


class ModelReportMixinProtocol[M: Model](Protocol):
    model: M
    model_name: str
    model_field_names: Iterable[str]

    def model_row(self, obj: M) -> Iterable[str]: ...
    def model_data(self, objects: Iterable[M]) -> Iterable[str]: ...
    def model_report(self, objects: Iterable[M], **kwargs: Any) -> None: ...


class SelfProtocol[M: Model](ModelReportMixinProtocol, ReportMixinProtocol, Protocol):
    pass


class ModelReportMixin[M](ABC):
    """Mixin to generate a report for a model.

    ! Intended for use with ReportMixin, SubcommandMixin and BaseCommand
    """

    @property
    def noun(self) -> str:
        return self.model.__class__.__name__

    @property
    @abstractmethod
    def model(self) -> type[M]:
        raise NotImplementedError

    @property
    def model_name(self) -> str:
        return self.model.__name__

    @property
    def model_field_names(self) -> Sequence[str]:
        return [f.name for f in self.model._meta.get_fields()]  # type: ignore[attr-defined] # noqa: SLF001

    def model_row(self, obj: M) -> Sequence[str]:
        """Get a row of data for a report"""
        return [str(getattr(obj, field)) for field in self.model_field_names]

    def model_data(self, objects: Sequence[M]) -> Sequence[Sequence[str]]:
        """Get all the rows of data for a report"""
        return [self.model_row(obj) for obj in objects]

    def model_report(self: SelfProtocol, objects: Sequence[M], **kwargs: Any) -> None:
        """Output a report for the model."""
        self.report(headers=self.model_field_names, data=self.model_data(objects), **kwargs)
