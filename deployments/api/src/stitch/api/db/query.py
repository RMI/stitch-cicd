from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, field_validator

from stitch.api.entities import PaginationParams
from stitch.ogsi.model.types import (
    FieldStatus,
    LocationType,
    OGSISrcKey,
    PrimaryHydrocarbonGroup,
    ProductionConventionality,
)

Q_FIELDS: tuple[str, ...] = (
    "name",
    "name_local",
    "basin",
    "state_province",
    "region",
)

EXACT_MATCH_FIELDS: tuple[str, ...] = (
    *Q_FIELDS,
    "id",
    "country",
    "source",
    "field_status",
    "location_type",
    "production_conventionality",
    "primary_hydrocarbon_group",
)

SORTABLE_FIELDS: tuple[str, ...] = (
    *EXACT_MATCH_FIELDS,
    "discovery_year",
    "production_start_year",
    "fid_year",
    "latitude",
    "longitude",
)

DEFAULT_SORT_FIELD = "name"
DEFAULT_SORT_ORDER = "asc"


@dataclass(frozen=True)
class Pagination:
    offset: int = 0
    limit: int = 50


class OGFieldFilters(BaseModel):
    q: str | None = None
    id: int | None = None
    name: str | None = None
    name_local: str | None = None
    basin: str | None = None
    state_province: str | None = None
    region: str | None = None
    country: str | None = None
    source: OGSISrcKey | None = None
    field_status: FieldStatus | None = None
    location_type: LocationType | None = None
    production_conventionality: ProductionConventionality | None = None
    primary_hydrocarbon_group: PrimaryHydrocarbonGroup | None = None


class Ordering(BaseModel):
    sort_by: str = DEFAULT_SORT_FIELD
    sort_order: Literal["asc", "desc"] = DEFAULT_SORT_ORDER

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        if v not in SORTABLE_FIELDS:
            raise ValueError(
                f"Invalid sort_by: '{v}'. Must be one of: {SORTABLE_FIELDS}"
            )
        return v


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
