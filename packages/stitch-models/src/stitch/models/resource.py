from typing import Sequence, NamedTuple
from pydantic import BaseModel, Field

from stitch.models.source import SourcePayload, SourceRef


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
