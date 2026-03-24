"""Database integration tests for OilGasFieldSourceModel.execute_query()."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from stitch.api.db import og_field_resource_actions as resource_actions
from stitch.api.db.model import OilGasFieldSourceModel
from stitch.api.db.query import DBQuery, Pagination
from stitch.api.entities import User
from tests.factories import ResourceCreateFactory


class TestSourceModelExecuteQuery:
    """Integration tests for OilGasFieldSourceModel.execute_query() classmethod."""

    @pytest.fixture
    async def seeded_sources(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        """Create 3 resources (each with sources + active memberships)."""
        for name in ["Alpha", "Bravo", "Charlie"]:
            await resource_actions.create(
                session=seeded_integration_session,
                user=test_user,
                resource=og_create_res_fact(name=name),
            )

    @pytest.mark.anyio
    async def test_execute_query_paginates(
        self,
        seeded_integration_session: AsyncSession,
        seeded_sources,
    ):
        q = DBQuery(pagination=Pagination(offset=0, limit=2))
        models, total = await OilGasFieldSourceModel.execute_query(
            seeded_integration_session, q
        )

        assert total > 0
        assert len(models) == min(2, total)

    @pytest.mark.anyio
    async def test_execute_query_empty_table(
        self,
        seeded_integration_session: AsyncSession,
    ):
        models, total = await OilGasFieldSourceModel.execute_query(
            seeded_integration_session, DBQuery()
        )
        assert total == 0
        assert len(models) == 0
