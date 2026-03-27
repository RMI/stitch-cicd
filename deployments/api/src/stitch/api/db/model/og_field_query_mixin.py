"""Declarative mixin: shared OG field columns + query classmethods."""

from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Self

from sqlalchemy import (
    ColumnElement,
    Float,
    Integer,
    Select,
    String,
    asc,
    desc,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column

from stitch.api.entities import OGFieldQueryParams


@declarative_mixin
class OGFieldQueryMixin:
    """Shared OG field columns and query classmethods.

    Provides the full set of domain columns (aligned with OilGasFieldBase,
    minus owners/operators) and classmethods for filtered, sorted, paginated
    queries.  Subclasses may override ``_base_query`` to customise the FROM
    clause (e.g. adding joins) while inheriting conditions, sorting, and
    pagination logic.
    """

    # ------------------------------------------------------------------
    # Query field configuration
    # ------------------------------------------------------------------

    _q_fields: ClassVar[tuple[str, ...]] = (
        "name",
        "name_local",
        "basin",
        "state_province",
        "region",
    )

    _exact_match_fields: ClassVar[tuple[str, ...]] = (
        *_q_fields,
        "id",
        "country",
        "source",
        "field_status",
        "location_type",
        "production_conventionality",
        "primary_hydrocarbon_group",
    )

    # ------------------------------------------------------------------
    # Shared column declarations
    # ------------------------------------------------------------------

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True)
    name_local: Mapped[str | None] = mapped_column(String, nullable=True)
    state_province: Mapped[str | None] = mapped_column(String, nullable=True)
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    basin: Mapped[str | None] = mapped_column(String, nullable=True)
    reservoir_formation: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    discovery_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    production_start_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fid_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # location_type, production_conventionality, primary_hydrocarbon_group, and
    # field_status are declared by each subclass with their own types (Literal
    # enums on the source table, plain str on the coalesced view).
    # _build_conditions uses getattr so they work regardless.

    # ------------------------------------------------------------------
    # Public query classmethods
    # ------------------------------------------------------------------

    @classmethod
    async def query(
        cls,
        session: AsyncSession,
        params: OGFieldQueryParams,
    ) -> tuple[Sequence[Self], int]:
        """Execute a filtered, sorted, paginated query and return (rows, total)."""
        base = cls._base_query(params)
        total = (
            await session.scalar(select(func.count()).select_from(base.subquery())) or 0
        )
        stmt = cls._apply_pagination(base, params)
        rows = (await session.scalars(stmt)).all()
        return rows, total

    @classmethod
    async def count(
        cls,
        session: AsyncSession,
        params: OGFieldQueryParams | None = None,
    ) -> int:
        """Return the total number of matching rows (unfiltered when params is None)."""
        if params is None:
            stmt = select(func.count()).select_from(cls)
        else:
            stmt = select(func.count()).select_from(cls._base_query(params).subquery())
        return await session.scalar(stmt) or 0

    # ------------------------------------------------------------------
    # Internal helpers (overridable)
    # ------------------------------------------------------------------

    @classmethod
    def _base_query(cls, params: OGFieldQueryParams) -> Select[tuple[Self]]:
        """Filtered + sorted SELECT with no pagination.

        Override this in subclasses to modify the FROM clause (e.g. add joins).
        """
        stmt: Select[tuple[Self]] = select(cls).distinct()
        for cond in cls._build_conditions(params):
            stmt = stmt.where(cond)
        return cls._apply_sort(stmt, params)

    @classmethod
    def _build_conditions(cls, params: OGFieldQueryParams) -> list[ColumnElement[bool]]:
        """Build WHERE conditions from filter params."""
        conditions: list[ColumnElement[bool]] = []

        if params.q:
            q_term = f"%{params.q}%"
            q_conds: list[ColumnElement[bool]] = []
            for field_name in cls._q_fields:
                col = getattr(cls, field_name, None)
                if col is not None:
                    q_conds.append(col.ilike(q_term))
            if q_conds:
                conditions.append(or_(*q_conds))

        for field_name in cls._exact_match_fields:
            value = getattr(params, field_name, None)
            if value is not None:
                col = getattr(cls, field_name, None)
                if col is not None:
                    conditions.append(col == value)

        return conditions

    @classmethod
    def _apply_sort(
        cls, stmt: Select[tuple[Self]], params: OGFieldQueryParams
    ) -> Select[tuple[Self]]:
        """Apply ORDER BY with id tie-breaker."""
        sort_col = getattr(cls, params.sort_by)
        direction = desc if params.sort_order == "desc" else asc
        stmt = stmt.order_by(direction(sort_col).nulls_last())
        if params.sort_by != "id":
            stmt = stmt.order_by(asc(cls.id))
        return stmt

    @classmethod
    def _apply_pagination(
        cls, stmt: Select[tuple[Self]], params: OGFieldQueryParams
    ) -> Select[tuple[Self]]:
        """Apply offset/limit for pagination."""
        return stmt.offset(params.offset).limit(params.limit)
