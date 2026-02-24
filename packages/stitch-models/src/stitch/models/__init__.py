from typing import Sequence, NamedTuple, TypeVar, Mapping, MutableMapping
from pydantic import BaseModel, Field, ConfigDict

from .types import IdType

__all__ = [
    "Resource",
    "ResourceBase",
    "ConstituentProvenance",
    "SourceBase",
    "SourceCollection",
    "SourcePayload",
    "SourceRef",
    "MutableSourceCollection",
]


class SourceBase[TId: IdType, TSrcKey: str](BaseModel):
    id: TId
    source: TSrcKey

    model_config = ConfigDict(from_attributes=True)


TId = TypeVar("TId", bound=IdType)
TSrc = TypeVar("TSrc", bound=SourceBase)
SourceCollection = Mapping[TId, TSrc]
MutableSourceCollection = MutableMapping[TId, TSrc]


class SourcePayload(BaseModel):
    """Base for domain-specific source payload containers.

    Subclass and declare attributes typed as SourceCollection[TId, TSrc].
    """

    model_config = ConfigDict(from_attributes=True)


class SourceRef[TId: IdType, TSrcKey: str](NamedTuple):
    source: TSrcKey
    id: TId


class ResourceBase(BaseModel):
    name: str | None = Field(default=None)
    country: str | None = Field(default=None)
    repointed_to: "Resource | None" = Field(default=None)


class ConstituentProvenance[TSrcRef: SourceRef](NamedTuple):
    id: int
    source_refs: Sequence[TSrcRef]


class Resource[TSD: SourcePayload, TProv: ConstituentProvenance](ResourceBase):
    id: int
    source_data: TSD
    provenance: Sequence[TProv]
