from typing import Sequence, NamedTuple, TypeVar, Mapping, MutableMapping, Self
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
    repointed_to: Self | None = Field(default=None)


class ConstituentProvenance[TSrcRef: SourceRef](NamedTuple):
    """Maps resource identifier to source keys and ids to allow auditing of provenance for SourcePayloads"""

    id: int
    source_refs: Sequence[TSrcRef]


class Resource[TPayload: SourcePayload, TProv: ConstituentProvenance](ResourceBase):
    id: int
    source_data: TPayload
    provenance: Sequence[TProv]
    """Houses aggregate relationships between constituent/merged resources and their respective source payloads."""
