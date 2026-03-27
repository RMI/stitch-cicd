"""Integration tests for base_query against OilGasFieldSourceModel."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from stitch.api.db.model import OilGasFieldSourceModel
from stitch.api.db.query import base_query, count_query
from stitch.api.entities import (
    OGFieldFilterParams,
    OGFieldSortParams,
    PaginationParams,
    User,
)
from stitch.ogsi.model.types import OGSISrcKey


class _QueryParams(PaginationParams, OGFieldFilterParams, OGFieldSortParams):
    source: OGSISrcKey | None = None


@pytest.fixture
async def seeded_sources(
    seeded_integration_session: AsyncSession,
    test_user: User,
):
    """Seed 8 diverse source rows for query testing."""
    session = seeded_integration_session
    uid = test_user.id
    sources = [
        OilGasFieldSourceModel(
            source="gem", name="Permian Basin",
            country="USA", field_status="Producing", basin="Permian",
            region="Texas", discovery_year=1920,
            created_by_id=uid, last_updated_by_id=uid,
        ),
        OilGasFieldSourceModel(
            source="wm", name="Ghawar",
            country="SAU", field_status="Producing", location_type="Onshore",
            discovery_year=1948,
            created_by_id=uid, last_updated_by_id=uid,
        ),
        OilGasFieldSourceModel(
            source="gem", name="Vaca Muerta",
            country="ARG", field_status="Producing", basin="Neuquen",
            production_conventionality="Unconventional",
            created_by_id=uid, last_updated_by_id=uid,
        ),
        OilGasFieldSourceModel(
            source="rmi", name="Prudhoe Bay",
            country="USA", field_status="Non-Producing", region="Alaska",
            discovery_year=1968,
            created_by_id=uid, last_updated_by_id=uid,
        ),
        OilGasFieldSourceModel(
            source="wm", name="Kashagan",
            country="KAZ", field_status="Producing", location_type="Offshore",
            discovery_year=2000,
            created_by_id=uid, last_updated_by_id=uid,
        ),
        OilGasFieldSourceModel(
            source="gem", name="permskiy basseyn",
            country="RUS", name_local="\u043f\u0435\u0440\u043c\u0441\u043a\u0438\u0439 \u0431\u0430\u0441\u0441\u0435\u0439\u043d",
            field_status="Abandoned",
            created_by_id=uid, last_updated_by_id=uid,
        ),
        OilGasFieldSourceModel(
            source="llm", name="Daqing",
            country="CHN", field_status="Producing", discovery_year=1959,
            created_by_id=uid, last_updated_by_id=uid,
        ),
        OilGasFieldSourceModel(
            source="gem", name="Permian Delaware",
            country="USA", field_status="Producing", basin="Permian",
            state_province="New Mexico",
            created_by_id=uid, last_updated_by_id=uid,
        ),
    ]
    session.add_all(sources)
    await session.flush()
    return sources


async def _execute(session, **overrides):
    """Helper: run base_query + count_query against source table."""
    params = _QueryParams(**overrides)

    stmt = base_query(OilGasFieldSourceModel, params=params)
    count_stmt = count_query(OilGasFieldSourceModel, params=params)

    rows = (await session.scalars(stmt)).all()
    total = await session.scalar(count_stmt)
    return rows, total


class TestBaseQuerySubstringSearch:
    """Tests for q= substring matching across text fields."""

    @pytest.mark.anyio
    async def test_q_matches_name_and_name_local(
        self, seeded_integration_session, seeded_sources,
    ):
        """q='perm' matches 'Permian Basin', 'Permian Delaware', 'permskiy basseyn'."""
        rows, total = await _execute(
            seeded_integration_session,
            q="perm",
        )
        names = {r.name for r in rows}
        assert total == 3
        assert {"Permian Basin", "Permian Delaware", "permskiy basseyn"} == names

    @pytest.mark.anyio
    async def test_q_combined_with_exact_filter(
        self, seeded_integration_session, seeded_sources,
    ):
        """q='perm' + country='USA' narrows to 2 results."""
        rows, total = await _execute(
            seeded_integration_session,
            q="perm",
            country="USA",
        )
        names = {r.name for r in rows}
        assert total == 2
        assert {"Permian Basin", "Permian Delaware"} == names


class TestBaseQueryExactFilters:
    """Tests for exact-match equality filters."""

    @pytest.mark.anyio
    async def test_multiple_filters_and(
        self, seeded_integration_session, seeded_sources,
    ):
        """country=USA AND field_status=Producing returns Permian Basin, Permian Delaware."""
        rows, total = await _execute(
            seeded_integration_session,
            country="USA",
            field_status="Producing",
        )
        names = {r.name for r in rows}
        assert total == 2
        assert {"Permian Basin", "Permian Delaware"} == names

    @pytest.mark.anyio
    async def test_no_matches(
        self, seeded_integration_session, seeded_sources,
    ):
        """country=XYZ returns empty."""
        rows, total = await _execute(
            seeded_integration_session,
            country="XYZ",
        )
        assert total == 0
        assert len(rows) == 0

    @pytest.mark.anyio
    async def test_empty_q_ignored(
        self, seeded_integration_session, seeded_sources,
    ):
        """q='' treated as no search, returns all 8."""
        rows, total = await _execute(
            seeded_integration_session,
            q="",
        )
        assert total == 8


class TestBaseQuerySortAndPagination:
    """Tests for sorting and pagination."""

    @pytest.mark.anyio
    async def test_sort_and_paginate(
        self, seeded_integration_session, seeded_sources,
    ):
        """Sort by discovery_year asc, page_size=3 returns first 3 non-null years."""
        rows, total = await _execute(
            seeded_integration_session,
            sort_by="discovery_year",
            sort_order="asc",
            page=1,
            page_size=3,
        )
        assert total == 8
        assert len(rows) == 3
        years = [r.discovery_year for r in rows]
        assert years == [1920, 1948, 1959]

    @pytest.mark.anyio
    async def test_combined_filter_sort_paginate(
        self, seeded_integration_session, seeded_sources,
    ):
        """q=perm + field_status=Producing + sort by name desc + page_size=1."""
        rows, total = await _execute(
            seeded_integration_session,
            q="perm",
            field_status="Producing",
            sort_by="name",
            sort_order="desc",
            page=1,
            page_size=1,
        )
        assert total == 2
        assert len(rows) == 1
        assert rows[0].name == "Permian Delaware"

    @pytest.mark.anyio
    async def test_invalid_sort_field_raises(self):
        """OGFieldSortParams with invalid sort_by raises ValidationError."""
        with pytest.raises(Exception):
            OGFieldSortParams(sort_by="owners")
