import pydantic

from .types import Triple


class IngestPromptWithContextResponse(pydantic.BaseModel):
    triples: list[Triple]
    context_summary: str | None = None

    class Config:
        populate_by_name = True
        validate_by_name = True
