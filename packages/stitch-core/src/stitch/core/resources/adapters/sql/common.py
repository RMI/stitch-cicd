from typing import Protocol, TypeVar


T = TypeVar("T")

EntOrId = T | int


class HasId(Protocol):
    id: int


def extract_id(entity: HasId | int) -> int:
    if hasattr(entity, "id"):
        return entity.id
    return entity
