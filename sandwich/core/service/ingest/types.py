from __future__ import annotations

import pydantic

# These models use field aliases and Pydantic v2 config to accept both snake_case
# and camelCase (LLM/external) keys. This allows seamless ingestion of LLM output while keeping
# mypy happy.


class Entity(pydantic.BaseModel):
    entity_type: str = pydantic.Field(..., alias="entityType")
    node: dict[str, object]

    class Config:
        populate_by_name = True
        validate_by_name = True


class NormalizedPredicate(pydantic.BaseModel):
    predicate_type: str = pydantic.Field(..., alias="predicateType")
    traits: dict[str, bool] | None = None
    properties: dict[str, object] | None = None

    class Config:
        populate_by_name = True
        validate_by_name = True


class Triple(pydantic.BaseModel):
    subject: Entity
    predicate: str
    normalized_predicate: NormalizedPredicate = pydantic.Field(..., alias="normalizedPredicate")
    obj: Entity = pydantic.Field(..., alias="object")

    class Config:
        populate_by_name = True
        validate_by_name = True
