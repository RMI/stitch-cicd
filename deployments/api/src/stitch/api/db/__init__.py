from typing import override
from sqlalchemy.orm import Session
from stitch.core.resources.domain.ports import SourceRegistry, SourceRepository

from stitch.api.db.gem_repository import GemRepository


class FieldResourceRegistry(SourceRegistry):
    _sources: frozenset[str] = frozenset("str")
    _session: Session

    def __init__(self, session: Session) -> None:
        self._session = session

    @override
    def is_source(self, name: str) -> bool:
        return name in self._sources

    @override
    def get_source_repository(self, source: str) -> SourceRepository:
        if not self.is_source(source):
            raise Exception(f'No source found for "{source}".')

        return GemRepository(self._session)


def create_field_registry(session: Session) -> SourceRegistry:
    return FieldResourceRegistry(session)
