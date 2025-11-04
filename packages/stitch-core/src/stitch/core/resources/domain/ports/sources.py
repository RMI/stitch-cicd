from collections.abc import Sequence, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import (
    Any,
    Protocol,
    Required,
    TypedDict,
    Unpack,
)

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class SourceRecord:
    id: int
    dataset: str
    name: str | None
    country_iso3: str | None
    operator_name: str | None
    latitude: float | None
    longitude: float | None
    payload: object | Mapping[str, Any]
    created: datetime


class SourceRecordData(TypedDict, total=False):
    dataset: Required[str]
    payload: Required[object | Mapping[str, Any]]
    name: str | None
    country_iso3: str | None
    operator: str | None
    latitude: float | None
    longitude: float | None


class SourcePersistenceRepository(Protocol):
    @property
    def source_name(self) -> str:
        """Unique collection/table identifier."""

    def write(
        self,
        entity_data: SourceRecordData | None = None,
        /,
        **kwargs: Unpack[SourceRecordData],
    ) -> str:
        """Persist record and return new id"""

    def fetch(self, source_id: str) -> SourceRecord | None:
        """Retrieve entity record by id. Return `None` if it doesn't exist."""
        pass

    def fecth_many(self, source_ids: list[str]) -> Sequence[SourceRecord]:
        """Retrieve multiple source entities"""

    def row_to_record_data(self, data: Mapping[str, Any]) -> SourceRecordData:
        """Translate source data to record data structure."""


class SourceRegistry(Protocol):
    def is_source(self, name: str) -> bool:
        """Check if a name exist as a source."""

    def get_source_repository(self, source_name: str) -> SourcePersistenceRepository:
        """Fetch a source data access repository"""


class SourceRegistryFactory(Protocol):
    def __call__(self, session: Session) -> SourceRegistry:
        pass
