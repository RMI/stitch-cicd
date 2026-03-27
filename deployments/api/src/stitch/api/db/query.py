from sqlalchemy import Select, asc, desc, func, or_, select

from stitch.api.db.model.common import Base

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


def base_query[T: Base](
    table: type[T],
    *,
    params,
) -> Select:
    """Build a filtered, sorted, paginated SELECT.

    Works against any table or view exposing OilGasFieldBase columns.
    """
    stmt = select(table)
    for cond in build_conditions(table, params):
        stmt = stmt.where(cond)

    sort_col = getattr(table, params.sort_by)
    direction = desc if params.sort_order == "desc" else asc
    stmt = stmt.order_by(direction(sort_col).nulls_last())
    if params.sort_by != "id":
        stmt = stmt.order_by(asc(table.id))

    stmt = stmt.offset(params.offset).limit(params.limit)
    return stmt


def count_query[T: Base](table: type[T], *, params) -> Select:
    """Build a COUNT query with the same filter conditions as base_query."""
    stmt = select(func.count()).select_from(table)
    for cond in build_conditions(table, params):
        stmt = stmt.where(cond)
    return stmt


def build_conditions[T: Base](table: type[T], params) -> list:
    """Build WHERE conditions from filter params."""
    conditions = []

    q = getattr(params, "q", None)
    if q:
        q_term = f"%{q}%"
        q_conditions = []
        for field_name in Q_FIELDS:
            col = getattr(table, field_name, None)
            if col is not None:
                q_conditions.append(col.ilike(q_term))
        if q_conditions:
            conditions.append(or_(*q_conditions))

    for field_name in EXACT_MATCH_FIELDS:
        value = getattr(params, field_name, None)
        if value is not None:
            col = getattr(table, field_name, None)
            if col is not None:
                conditions.append(col == value)

    return conditions
