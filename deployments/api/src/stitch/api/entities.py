from __future__ import annotations
from collections.abc import Sequence
from datetime import datetime
from typing import (
    Annotated,
    Generic,
    Literal,
    Mapping,
    Protocol,
    Self,
    TypeVar,
    runtime_checkable,
)
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

IdType = int | str | UUID


@runtime_checkable
class HasId(Protocol):
    @property
    def id(self) -> IdType: ...


TSourceKey = TypeVar("TSourceKey", bound=str)


class SourceBase(BaseModel, Generic[TSourceKey]):
    source: TSourceKey


GEM_SRC = Literal["gem"]
WM_SRC = Literal["wm"]
RMI_SRC = Literal["rmi"]
CC_SRC = Literal["cc"]

SourceKey = GEM_SRC | WM_SRC | RMI_SRC | CC_SRC


class GemSource(SourceBase[GEM_SRC]):
    source: GEM_SRC = "gem"
    id: int
    name: str
    lat: float
    lon: float
    country: str


class WMSource(SourceBase[WM_SRC]):
    source: WM_SRC = "wm"
    id: int
    field_name: str
    field_country: str
    production: float


class ManualSource(SourceBase[RMI_SRC]):
    source: RMI_SRC = "rmi"
    id: int
    name_override: str
    gwp: float
    gor: float = Field(gt=0, lt=1)
    country: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class CCReservoirsSource(SourceBase[CC_SRC]):
    source: CC_SRC = "cc"
    id: int
    name: str
    basin: str
    depth: float
    geofence: Sequence[tuple[float, float]]


OGSISourcePayload = Annotated[
    GemSource | WMSource | ManualSource | CCReservoirsSource,
    Field(discriminator="source"),
]


class ResourceBase(BaseModel):
    name: str | None = Field(default=None)
    country: str | None = Field(default=None)
    repointed_to: Resource | None = Field(default=None)


class Resource(ResourceBase):
    id: int
    source_data: Mapping[tuple[SourceKey, str], OGSISourcePayload]
    constituents: Sequence[Self]
    created: datetime
    updated: datetime


class CreateResource(ResourceBase):
    source: str
    source_pk: str
    data: OGSISourcePayload


class User(BaseModel):
    id: int = Field(...)
    role: str | None = None
    email: EmailStr
    name: str
