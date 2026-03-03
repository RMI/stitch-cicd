from __future__ import annotations

from pydantic import BaseModel, Field
from stitch.models import BaseResource, EmptySourcePayload


class CreateResource(BaseModel):
    """Domain-agnostic create model."""

    # optional generic metadata; domains can replace/extend later
    label: str | None = None


class Resource(BaseModel):
    """Domain-agnostic read model."""

    resource: BaseResource[int] = Field(
        default_factory=lambda: BaseResource[int](source_data=EmptySourcePayload())
    )
    label: str | None = None
