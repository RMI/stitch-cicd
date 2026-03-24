"""Database integration tests for domain-agnostic resource_actions."""

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from stitch.api.db import og_field_resource_actions as resource_actions
from stitch.api.db.model import ResourceModel
from stitch.api.db.query import DBQuery, Pagination
from stitch.api.entities import User
from tests.factories import ResourceCreateFactory


class TestCreateResourceActionIntegration:
    """Integration tests for resource_actions.create() with real database."""

    @pytest.mark.anyio
    async def test_creates_resource_with_minimal_payload(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        resource_in = og_create_res_fact()

        result = await resource_actions.create(
            session=seeded_integration_session,
            user=test_user,
            resource=resource_in,
        )

        assert result.id is not None

        db_resource = await seeded_integration_session.get(ResourceModel, result.id)
        assert db_resource is not None

    @pytest.mark.anyio
    async def test_creates_resource_with_label(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        resource_in = og_create_res_fact(name="Test Label")

        result = await resource_actions.create(
            session=seeded_integration_session,
            user=test_user,
            resource=resource_in,
        )

        assert result.id is not None
        assert result.view is not None
        assert result.view.name == "Test Label"

        db_resource = await seeded_integration_session.get(ResourceModel, result.id)
        assert db_resource is not None
        # DB ResourceModel may store `.name`; tolerate either while refactor settles.
        assert getattr(db_resource, "name", None) in (None, "Test Label")


class TestGetResourceActionIntegration:
    """Integration tests for resource_actions.get() with real database."""

    @pytest.mark.anyio
    async def test_get_returns_resource(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        res = og_create_res_fact(name="Get Test")
        created = await resource_actions.create(
            session=seeded_integration_session,
            user=test_user,
            resource=res,
        )

        result = await resource_actions.get(
            session=seeded_integration_session,
            id=created.id,
        )

        assert result.id == created.id
        assert result.view is not None
        assert result.view.name == "Get Test"

    @pytest.mark.anyio
    async def test_get_nonexistent_raises_404(
        self,
        seeded_integration_session: AsyncSession,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await resource_actions.get(
                session=seeded_integration_session,
                id=99999,
            )
        assert exc_info.value.status_code == 404


class TestListResourcesActionIntegration:
    """Integration tests for resource_actions.get_all() with real database."""

    @pytest.mark.anyio
    async def test_get_all_returns_sequence(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        # create a couple resources
        await resource_actions.create(
            session=seeded_integration_session,
            user=test_user,
            resource=og_create_res_fact(name="A"),
        )
        await resource_actions.create(
            session=seeded_integration_session,
            user=test_user,
            resource=og_create_res_fact(name="B"),
        )

        results = await resource_actions.get_all(session=seeded_integration_session)
        assert isinstance(results, (list, tuple))
        assert len(results) >= 2

        labels = {r.view.name for r in results if r.view is not None}
        assert {"A", "B"} <= labels


class TestQueryResourcesActionIntegration:
    """Integration tests for resource_actions.query() with real database."""

    @pytest.mark.anyio
    async def test_query_returns_paginated_results(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        # Create 3 resources
        for name in ["A", "B", "C"]:
            await resource_actions.create(
                session=seeded_integration_session,
                user=test_user,
                resource=og_create_res_fact(name=name),
            )

        items, total_count = await resource_actions.query(
            seeded_integration_session, DBQuery(pagination=Pagination(offset=0, limit=2))
        )

        assert total_count == 3
        assert len(items) == 2

    @pytest.mark.anyio
    async def test_query_second_page(
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

        items, total_count = await resource_actions.query(
            seeded_integration_session, DBQuery(pagination=Pagination(offset=2, limit=2))
        )

        assert total_count == 3
        assert len(items) == 1

    @pytest.mark.anyio
    async def test_query_page_beyond_total(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        await resource_actions.create(
            session=seeded_integration_session,
            user=test_user,
            resource=og_create_res_fact(name="Only"),
        )

        items, total_count = await resource_actions.query(
            seeded_integration_session, DBQuery(pagination=Pagination(offset=4900, limit=50))
        )

        assert total_count == 1
        assert len(items) == 0

    @pytest.mark.anyio
    async def test_query_empty_table(
        self,
        seeded_integration_session: AsyncSession,
    ):
        items, total_count = await resource_actions.query(
            seeded_integration_session, DBQuery()
        )

        assert total_count == 0
        assert len(items) == 0


class TestResourceModelExecuteQuery:
    """Integration tests for ResourceModel.execute_query() classmethod."""

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
        models, total = await ResourceModel.execute_query(
            seeded_integration_session, q
        )

        assert total == 3
        assert len(models) == 2

    @pytest.mark.anyio
    async def test_execute_query_offset(
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

        q = DBQuery(pagination=Pagination(offset=2, limit=10))
        models, total = await ResourceModel.execute_query(
            seeded_integration_session, q
        )

        assert total == 3
        assert len(models) == 1

    @pytest.mark.anyio
    async def test_execute_query_empty(
        self,
        seeded_integration_session: AsyncSession,
    ):
        q = DBQuery()
        models, total = await ResourceModel.execute_query(
            seeded_integration_session, q
        )

        assert total == 0
        assert len(models) == 0
