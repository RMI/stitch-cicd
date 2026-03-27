"""Coalesced resource view: priority-based COALESCE over source fields."""

from __future__ import annotations

from sqlalchemy import String, case, func, select, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Mapped, mapped_column
from stitch.ogsi.model.og_field import OilGasFieldBase

from .common import Base
from .og_field_query_mixin import OGFieldQueryMixin
from .og_field_source_priority import DEFAULT_PRIORITIES, OGFieldSourcePriority
from .oil_gas_field_source import OilGasFieldSourceModel
from .resource import MembershipModel, MembershipStatus, ResourceModel


def build_view_select(num_priorities: int = 4):
    """Build the SELECT statement for the coalesced resource view.

    Uses a pivot pattern: JOIN resources -> memberships -> sources -> priority,
    GROUP BY resource_id, COALESCE(MAX(CASE WHEN priority=N THEN col)) for each field.
    """
    s = OilGasFieldSourceModel
    m = MembershipModel
    r = ResourceModel
    p = OGFieldSourcePriority

    base = (
        select(r.id.label("id"))
        .join(m, m.resource_id == r.id)
        .join(s, m.source_pk == s.id)
        .join(p, s.source == p.source)
        .where(m.status == MembershipStatus.ACTIVE)
        .where(r.repointed_id.is_(None))
        .group_by(r.id)
    )

    for field_name in OilGasFieldBase.model_fields:
        if field_name in {"owners", "operators"}:
            continue
        col = getattr(s, field_name, None)
        if col is None:
            continue
        coalesce_args = [
            func.max(case((p.priority == i, col))) for i in range(1, num_priorities + 1)
        ]
        base = base.add_columns(func.coalesce(*coalesce_args).label(field_name))

    return base


async def create_view(engine: AsyncEngine) -> None:
    """Seed the priority table and create the SQL view."""
    async with engine.begin() as conn:
        for row in DEFAULT_PRIORITIES:
            await conn.execute(
                OGFieldSourcePriority.__table__.insert().prefix_with("OR IGNORE"),
                row,
            )

        view_select = build_view_select(num_priorities=len(DEFAULT_PRIORITIES))
        compiled = view_select.compile(
            dialect=conn.dialect, compile_kwargs={"literal_binds": True}
        )
        await conn.execute(
            text(f"CREATE VIEW IF NOT EXISTS resource_coalesced_view AS {compiled}")
        )


class ResourceCoalescedView(OGFieldQueryMixin, Base):
    __tablename__ = "resource_coalesced_view"
    __table_args__ = {"info": {"is_view": True}}

    location_type: Mapped[str | None] = mapped_column(String, nullable=True)
    production_conventionality: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    primary_hydrocarbon_group: Mapped[str | None] = mapped_column(String, nullable=True)
    field_status: Mapped[str | None] = mapped_column(String, nullable=True)
