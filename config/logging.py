import datetime
import logging
import os
from typing import Any

import tzlocal
from django_datadog_logger.formatters.datadog import DataDogJSONFormatter


class CustomDataDogJSONFormatter(DataDogJSONFormatter):
    def json_record(self, *args: Any, **kwargs: Any) -> dict[str, str]:
        log_entry_dict = super().json_record(*args, **kwargs)
        # Remove PII
        log_entry_dict.pop("usr.name", None)
        log_entry_dict.pop("usr.email", None)
        return log_entry_dict


class ProcrastinateBlueprintFilter(logging.Filter):
    """Filter out Procrastinate's Blueprint info log message.

    This message is logged anytime a django management command is run,
    which is starting to clutter the logs and is frankly annoying to see.

    We aren't using blueprints yet. This message is not helpful.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return record.msg != "Adding tasks from blueprint"


def real_local_timezone() -> datetime.tzinfo:
    """We configure Django to always use UTC, but want to use the local timezone for local logging."""
    tz = os.environ.pop("TZ", None)
    try:
        return tzlocal.get_localzone()
    finally:
        if tz is not None:
            os.environ["TZ"] = tz


class ColorPrettyFormatter(CustomDataDogJSONFormatter):
    LEVEL_COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m\033[97m",  # White on Red BG
    }
    RESET = "\033[0m"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._timezone = real_local_timezone()

    def to_json(self, record: dict[str, Any]) -> str:
        # every record has these attributes
        message = record.pop("message")
        date = record.pop("date")
        status = record.pop("status")
        logger_name = record.pop("logger.name")
        _logger_thread_name = record.pop("logger.thread_name")
        _logger_method_name = record.pop("logger.method_name")

        date = datetime.datetime.fromisoformat(date).astimezone(self._timezone)
        level_color = self.LEVEL_COLORS.get(status, "")
        reset = self.RESET if level_color else ""
        result = f"{date:%Y-%m-%d %H:%M:%S.%f} {logger_name} {level_color}{status}{reset} {message}"

        # if there are additional attributes, add them to the log message
        if record:
            result += f" | {super().to_json(record)}"

        return result
