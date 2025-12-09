from collections.abc import Mapping, Sequence
import copy
from datetime import datetime
from typing import Any, ClassVar, Unpack, override
from sqlalchemy.orm import Session
from stitch.core.resources.domain.entities import SourceEntity, SourceRecord
from stitch.core.resources.domain.ports import SourceRepository

_dummy_db: dict[int, SourceEntity] = {}


def _next_id():
    return len(_dummy_db)


class GemRepository(SourceRepository):
    _session: Session

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    @override
    def source_name(self) -> str:
        return "gem"

    @override
    def write(
        self, entity_data: SourceRecord | None = None, /, **kwargs: Unpack[SourceRecord]
    ) -> str:
        rec = entity_data if entity_data is not None else kwargs
        id_ = _next_id()
        _dummy_db[id_] = SourceEntity(id=id_, **rec, created=datetime.now())
        return str(id_)

    @override
    def fecth_many(self, source_pks: Sequence[str]) -> Sequence[SourceEntity]:
        return [_dummy_db[int(id_)] for id_ in source_pks if int(id_) in _dummy_db]

    @override
    def fetch(self, source_pk: str) -> SourceEntity | None:
        return _dummy_db.get(int(source_pk), None)

    @override
    def row_to_record_data(self, data: Mapping[str, Any]) -> SourceRecord:
        payload = copy.deepcopy(data)
        name: str = data.get("Unit ID", "name")
        return SourceRecord(
            source="gem",
            name=name,
            country=str(data.get("Country/Area", "US")),
            latitude=float(data.get("Latitude", "0.0")),
            longitude=float(data.get("Longitude", "0.0")),
            payload=payload,
        )
