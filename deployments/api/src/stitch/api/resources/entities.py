from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateResource(BaseModel):
    """Domain-agnostic create model."""

    model_config = ConfigDict(extra="forbid")
    name: str | None = None


class Resource(BaseModel):
    """Domain-agnostic read model."""

    id: int
    name: str | None = None
    repointed_to: int | None = None
    constituents: frozenset[int] = Field(default_factory=frozenset)
