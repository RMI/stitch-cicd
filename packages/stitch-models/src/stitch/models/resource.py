from typing import Sequence
from typing_extensions import Self
from pydantic import BaseModel, Field

from stitch.models.source import SourcePayload


class ResourceBase(BaseModel):
    name: str | None = Field(default=None)
    country: str | None = Field(default=None)
    repointed_to: "Resource | None" = Field(default=None)


class Resource[TSD: SourcePayload](ResourceBase):
    id: int
    source_data: TSD
    constituents: Sequence[Self]
