"""Database integration tests for og_field_source_actions."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from stitch.api.db import og_field_resource_actions as resource_actions
from stitch.api.db import og_field_source_actions as source_actions
from stitch.api.db.query import DBQuery, Pagination
from stitch.api.entities import User
from tests.factories import ResourceCreateFactory


class TestQuerySourcesActionIntegration:
    """Integration tests for og_field_source_actions.query() with real database."""

    @pytest.mark.anyio
    async def test_query_returns_paginated_results(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        # Create resources (each gets at least 1 source via factory)
        for name in ["A", "B", "C"]:
            await resource_actions.create(
                session=seeded_integration_session,
                user=test_user,
                resource=og_create_res_fact(name=name),
            )

        # Get total to know how many sources exist
        _, full_count = await source_actions.query(
            seeded_integration_session, DBQuery(pagination=Pagination(offset=0, limit=100))
        )

        # Now paginate with smaller page_size
        items, total_count = await source_actions.query(
            seeded_integration_session, DBQuery(pagination=Pagination(offset=0, limit=2))
        )

        assert total_count == full_count
        assert len(items) == min(2, full_count)

    @pytest.mark.anyio
    async def test_query_empty_table(
        self,
        seeded_integration_session: AsyncSession,
    ):
        items, total_count = await source_actions.query(
            seeded_integration_session, DBQuery()
        )

        assert total_count == 0
        assert len(items) == 0


from stitch.api.db.model import OilGasFieldSourceModel


class TestSourceModelExecuteQuery:
    """Integration tests for OilGasFieldSourceModel.execute_query() classmethod."""

    @pytest.mark.anyio
    async def test_execute_query_paginates(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        for name in ["A", "B", "C"]:
            await resource_actions.create(
                session=seeded_integration_session,
                user=test_user,
                resource=og_create_res_fact(name=name),
            )

        q = DBQuery(pagination=Pagination(offset=0, limit=2))
        models, total = await OilGasFieldSourceModel.execute_query(
            seeded_integration_session, q
        )

        assert total > 0
        assert len(models) == min(2, total)

    @pytest.mark.anyio
    async def test_execute_query_empty(
        self,
        seeded_integration_session: AsyncSession,
    ):
        q = DBQuery()
        models, total = await OilGasFieldSourceModel.execute_query(
            seeded_integration_session, q
        )

        assert total == 0
        assert len(models) == 0
