from collections import defaultdict
from typing import (
    ClassVar,
    Hashable,
)

from pydantic import BaseModel, ConfigDict, Field

from .types import IdType, Provenance

__all__ = [
    "Resource",
    "Source",
    "SourcePayload",
]


class Source[TId: IdType, TSrcKey: str](BaseModel):
    """Base class for dependent, canonical `Source` data declarations.

    Used for creational patterns and to handle use cases where identifiers should NOT be present.

    Attributes:
        source: key for identifying the data source
    """

    id: TId | None = None
    source: TSrcKey

    # we set `from_attributes=True` to accommodate ORM or other object mappings
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class SourcePayload(BaseModel):
    """Base for domain-specific source payload containers.

    Subclass and declare attributes typed as SourceCollection[TId, TSrc].
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class Resource[
    TResId: IdType,
    TSrcId: IdType,
    TSrcKey: str,
    TPayload: SourcePayload,
](BaseModel):
    id: TResId | None = None
    source_data: TPayload
    repointed_to: Hashable | None = Field(default=None)
    provenance: Provenance[TResId, TSrcId, TSrcKey] = Field(
        default_factory=lambda: defaultdict(list)
    )
