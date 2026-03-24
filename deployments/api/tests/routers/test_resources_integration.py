"""Integration tests for resources router with real SQLite database."""

from httpx import AsyncClient
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import ResourceCreateFactory, SourceFactory
from stitch.api.db.model import ResourceModel


class TestResourcesIntegration:
    """Integration tests for resources endpoints with real database."""

    @pytest.mark.anyio
    async def test_get_nonexistent_returns_404(self, integration_client):
        """GET /resources/999 returns 404 status code."""
        response = await integration_client.get("/oil-gas-fields/999")

        assert response.status_code == 404
        assert "999" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_create_resource_returns_resource(
        self,
        integration_client: AsyncClient,
        og_create_res_fact: ResourceCreateFactory,
    ):
        """POST /resources/ returns the created resource."""
        resource_in = og_create_res_fact(name="Integration Test Resource")

        response = await integration_client.post(
            "/oil-gas-fields/", json=resource_in.model_dump(mode="json")
        )

        assert response.status_code == 200
        data = response.json()
        assert data["view"]["name"] == "Integration Test Resource"
        assert "id" in data
        assert data["id"] > 0

    @pytest.mark.anyio
    async def test_create_and_get_resource(
        self,
        integration_client: AsyncClient,
        og_create_res_fact: ResourceCreateFactory,
    ):
        """POST creates resource, GET retrieves it."""
        resource_in = og_create_res_fact(name="Roundtrip Resource")

        create_response = await integration_client.post(
            "/oil-gas-fields/", json=resource_in.model_dump(mode="json")
        )

        assert create_response.status_code == 200
        created_id = create_response.json()["id"]

        get_response = await integration_client.get(f"/oil-gas-fields/{created_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == created_id
        assert data["name"] == "Roundtrip Resource"

    @pytest.mark.anyio
    async def test_create_persists_to_database(
        self,
        integration_client: AsyncClient,
        integration_session_factory: async_sessionmaker[AsyncSession],
        og_create_res_fact: ResourceCreateFactory,
    ):
        """POST resource is persisted and queryable directly."""
        resource_in = og_create_res_fact(name="Persisted Resource")

        response = await integration_client.post(
            "/oil-gas-fields/", json=resource_in.model_dump(mode="json")
        )

        assert response.status_code == 200
        created_id = response.json()["id"]

        async with integration_session_factory() as session:
            result = await session.execute(
                select(ResourceModel).where(ResourceModel.id == created_id)
            )
            resource = result.scalar_one_or_none()
            assert resource is not None
            assert resource.id is not None

            sources = await resource.get_source_data(session)

        assert len(sources) > 0
        rmi_sources = [src for src in sources if src.source == "rmi"]
        assert len(rmi_sources) == 1
        assert rmi_sources[0].name == "Persisted Resource"

    @pytest.mark.anyio
    async def test_create_with_minimal_data(
        self,
        integration_client: AsyncClient,
        og_create_res_fact: ResourceCreateFactory,
        source_maker: SourceFactory,
    ):
        """POST /resources/ works with only required fields (no source data)."""
        resource_in = og_create_res_fact(name="Minimal Name", sources=[])

        response = await integration_client.post(
            "/oil-gas-fields/", json=resource_in.model_dump(mode="json")
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] > 0
        assert (view := data.get("view", None)) is not None
        assert view["name"] == "Minimal Name"


class TestGetAllResourcesIntegration:
    """Integration tests for GET /oil-gas-fields/ paginated endpoint."""

    @pytest.mark.anyio
    async def test_list_returns_paginated_envelope(
        self,
        integration_client: AsyncClient,
        og_create_res_fact: ResourceCreateFactory,
    ):
        # Create 3 resources
        for name in ["X", "Y", "Z"]:
            await integration_client.post(
                "/oil-gas-fields/", json=og_create_res_fact(name=name).model_dump(mode="json")
            )

        response = await integration_client.get("/oil-gas-fields/?page=1&page_size=2")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 3
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.anyio
    async def test_default_params_work(
        self,
        integration_client: AsyncClient,
    ):
        response = await integration_client.get("/oil-gas-fields/")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 50
        assert "items" in data
        assert "total_count" in data
