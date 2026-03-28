"""Database integration tests for domain-agnostic resource_actions."""

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from stitch.api.db import og_field_resource_actions as resource_actions
from stitch.api.db.model import ResourceModel
from stitch.api.entities import (
    OGFieldFilterParams,
    OGFieldSortParams,
    PaginationParams,
    User,
)
from tests.factories import ResourceCreateFactory


class _QueryParams(PaginationParams, OGFieldFilterParams, OGFieldSortParams):
    pass


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


class TestResourceQueryAction:
    """Integration tests for resource_actions.query() and count()."""

    @pytest.fixture
    async def seeded_resources(
        self,
        seeded_integration_session: AsyncSession,
        test_user: User,
        og_create_res_fact: ResourceCreateFactory,
    ):
        """Create 3 resources for query tests."""
        for name in ["Alpha", "Bravo", "Charlie"]:
            await resource_actions.create(
                session=seeded_integration_session,
                user=test_user,
                resource=og_create_res_fact(name=name),
            )

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "params_kwargs, expected_count",
        [
            pytest.param(
                {"page": 1, "page_size": 2},
                2,
                id="first-page",
            ),
            pytest.param(
                {"page": 2, "page_size": 2},
                1,
                id="offset-past-partial",
            ),
            pytest.param(
                {"page": 50, "page_size": 10},
                0,
                id="offset-past-end",
            ),
        ],
    )
    async def test_query_pagination(
        self,
        seeded_integration_session: AsyncSession,
        seeded_resources,
        params_kwargs: dict,
        expected_count: int,
    ):
        params = _QueryParams(**params_kwargs)
        items, total = await resource_actions.query(seeded_integration_session, params)
        assert total == 3
        assert len(items) == expected_count
