from __future__ import annotations
from collections.abc import Mapping
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class ResourceBase(BaseModel):
    name: str | None
    country: str | None
    repointed_to: ResourceOut | None


class ResourceOut(ResourceBase):
    id: int
    source_data: Mapping[str, Mapping[str, Any]]
    created: datetime
    updated: datetime


class CreateResource(ResourceBase):
    source: str
    source_pk: str
    data: Mapping[str, Any]
