from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from stitch.api.resources.entities import CreateResource, Resource as ResourceView


class CreateOilGasField(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource: CreateResource
    owner: str | None = Field(default=None)
    operator: str | None = Field(default=None)


class OilGasField(BaseModel):
    id: int
    resource: ResourceView
    owner: str | None = None
    operator: str | None = None
