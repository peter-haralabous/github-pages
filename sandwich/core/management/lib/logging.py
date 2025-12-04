import json
import pprint
from typing import Any
from typing import Literal
from typing import Protocol

from django.core.management.base import OutputWrapper

from sandwich.core.management.lib.base import BaseCommandProtocol
from sandwich.core.management.lib.json import jsonable_object

Verbosity = Literal[0, 1, 2, 3]


class LoggingCommandProtocol(BaseCommandProtocol, Protocol):
    def configure(self, *args: Any, **options: Any) -> Any: ...

    def critical(self, message: str) -> None: ...

    def error(self, message: str) -> None: ...

    def warning(self, message: str) -> None: ...

    def info(self, message: str) -> None: ...

    def verbose(self, message: str) -> None: ...

    def debug(self, message: str) -> None: ...

    def output(self, message: str) -> None: ...

    CRITICAL: Verbosity
    ERROR: Verbosity
    WARNING: Verbosity
    INFO: Verbosity
    VERBOSE: Verbosity
    DEBUG: Verbosity


class LoggingMixin:
    messages: list[tuple[str, str]] = []
    verbosity: Verbosity
    stdout: OutputWrapper
    stderr: OutputWrapper

    CRITICAL: Verbosity = 0
    ERROR: Verbosity = 0
    WARNING: Verbosity = 1
    INFO: Verbosity = 1
    VERBOSE: Verbosity = 2
    DEBUG: Verbosity = 3

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.stderr.style_func = lambda x: x

    def execute(self, *args: Any, **options: Any) -> Any:
        """Deal with configuration before handing off to handler"""
        self.configure(**options)
        return super().execute(*args, **options)  # type: ignore[misc]

    def configure(self, verbosity: Verbosity | None = None, **options: Any) -> None:
        self.verbosity = 1 if verbosity is None else verbosity

    def critical(self, message: str) -> None:
        self.log(message, self.CRITICAL)

    def error(self, message: str) -> None:
        self.log(message, self.ERROR)

    def warning(self, message: str) -> None:
        self.log(message, self.WARNING)

    def info(self, message: str) -> None:
        self.log(message, self.INFO)

    def verbose(self, message: str) -> None:
        self.log(message, self.VERBOSE)

    def debug(self, message: str) -> None:
        self.log(message, self.DEBUG)

    def log(self, message: str, verbosity: Verbosity) -> None:
        """
        Write message to stderr to allow data passed on stdout

        See also: https://docs.djangoproject.com/en/5.0/ref/django-admin/#cmdoption-verbosity
        """
        if verbosity <= self.verbosity:
            self.stderr.write(message)

    def output(self, message: str) -> None:
        self.stdout.write(message)

    def json(self, obj: Any, indent: int = 2, log: Verbosity | None = None, **kwargs: Any) -> None:
        message = json.dumps(obj, indent=indent, default=jsonable_object, **kwargs)
        if log:
            self.log(message, verbosity=log)
        else:
            self.output(message)

    def format(self, value: Any, **kwargs: Any) -> str:
        return pprint.pformat(value, **kwargs)
