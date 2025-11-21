from django.forms.utils import ErrorDict
from pydantic import BaseModel
from pydantic import ConfigDict


class ErrorResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    errors: ErrorDict
