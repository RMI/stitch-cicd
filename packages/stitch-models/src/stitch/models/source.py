from sqlalchemy.util.typing import TypedDict
from typing import TypeVar, Mapping, NamedTuple, MutableMapping, Literal
from pydantic import BaseModel, ConfigDict

from .common import IdType


class SourceBase[TId: IdType, TSrcKey: str](BaseModel):
    id: TId
    source: TSrcKey

    model_config = ConfigDict(from_attributes=True)


TId = TypeVar("TId", bound=IdType)
TSrc = TypeVar("TSrc", bound=SourceBase)
SourceCollection = Mapping[TId, TSrc]
MutableSourceCollection = MutableMapping[TId, TSrc]


class SourceData[TId: IdType, TSrcKey: str, TSrcCls: SourceBase](
    TypedDict[TSrcKey, SourceCollection[TId, TSrcCls]]
): ...


class SourceRef[TId: IdType, TSrcKey: str](NamedTuple):
    source: TSrcKey
    id: TId
