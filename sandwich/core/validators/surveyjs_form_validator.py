import json
import logging
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from jsonschema import ValidationError as SchemaError
from jsonschema import validate

logger = logging.getLogger(__name__)

default_schema_path = Path(settings.BASE_DIR) / "sandwich/core/validators/schema/generated_surveyjs_definition.json"


def validate_survey_json(data: dict, schema_path: Path = default_schema_path) -> None:
    """
    Validates data directly against the JSON schema file.
    """
    json_schema = None
    try:
        with Path.open(schema_path) as f:
            json_schema = json.load(f)
    except FileNotFoundError:
        logger.debug(
            "Could not open schema file",
            extra={
                "path": schema_path,
            },
        )

    try:
        validate(instance=data, schema=json_schema)

    except SchemaError as e:
        error_message = f"Schema Error: {e.message}"

        raise ValidationError(error_message) from None
