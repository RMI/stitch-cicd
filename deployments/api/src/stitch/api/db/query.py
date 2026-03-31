from dataclasses import dataclass, field
from typing import Literal

from stitch.api.entities import PaginationParams


@dataclass(frozen=True)
class Pagination:
    offset: int = 0
    limit: int = 50


@dataclass(frozen=True)
class Ordering:
    sort_by: str | None = None
    sort_order: Literal["asc", "desc"] = "asc"


@dataclass(frozen=True)
class DBQuery[F]:
    pagination: Pagination = field(default_factory=Pagination)
    ordering: Ordering = field(default_factory=Ordering)
    filters: F | None = None


def pagination_to_db(params: PaginationParams) -> Pagination:
    return Pagination(
        offset=(params.page - 1) * params.page_size,
        limit=params.page_size,
    )
