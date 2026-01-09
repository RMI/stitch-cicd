"""Integration tests for resources router with real SQLite database."""

import pytest
from sqlalchemy import select

from stitch.api.db.model import ResourceModel


class TestResourcesIntegration:
    """Integration tests for resources endpoints with real database."""

    @pytest.mark.anyio
    async def test_get_nonexistent_returns_404(self, integration_client):
        """GET /resources/999 returns 404 status code."""
        response = await integration_client.get("/resources/999")

        assert response.status_code == 404
        assert "999" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_create_resource_returns_resource(self, integration_client):
        """POST /resources/ returns the created resource."""
        response = await integration_client.post(
            "/resources/",
            json={
                "name": "Integration Test Resource",
                "country": "USA",
                "source": "gem",
                "source_pk": "GEM-INT-001",
                "data": {
                    "source": "gem",
                    "id": 100,
                    "name": "GEM Integration Field",
                    "lat": 40.0,
                    "lon": -100.0,
                    "country": "USA",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Integration Test Resource"
        assert data["country"] == "USA"
        assert "id" in data
        assert data["id"] > 0

    @pytest.mark.anyio
    async def test_create_and_get_resource(self, integration_client):
        """POST creates resource, GET retrieves it."""
        create_response = await integration_client.post(
            "/resources/",
            json={
                "name": "Roundtrip Resource",
                "country": "CAN",
                "source": "wm",
                "source_pk": "WM-ROUND-001",
                "data": {
                    "source": "wm",
                    "id": 200,
                    "field_name": "WM Roundtrip Field",
                    "field_country": "CAN",
                    "production": 5000.0,
                },
            },
        )

        assert create_response.status_code == 200
        created_id = create_response.json()["id"]

        get_response = await integration_client.get(f"/resources/{created_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == created_id
        assert data["name"] == "Roundtrip Resource"
        assert data["country"] == "CAN"

    @pytest.mark.anyio
    async def test_create_persists_to_database(
        self, integration_client, integration_session_factory
    ):
        """POST resource is persisted and queryable directly."""
        response = await integration_client.post(
            "/resources/",
            json={
                "name": "Persisted Resource",
                "country": "MEX",
                "source": "gem",
                "source_pk": "GEM-PERSIST-001",
                "data": {
                    "source": "gem",
                    "id": 300,
                    "name": "GEM Persist Field",
                    "lat": 25.0,
                    "lon": -105.0,
                    "country": "MEX",
                },
            },
        )

        assert response.status_code == 200
        created_id = response.json()["id"]

        async with integration_session_factory() as session:
            result = await session.execute(
                select(ResourceModel).where(ResourceModel.id == created_id)
            )
            resource = result.scalar_one_or_none()

        assert resource is not None
        assert resource.name == "Persisted Resource"
        assert resource.country == "MEX"

    @pytest.mark.anyio
    async def test_create_with_minimal_data(self, integration_client):
        """POST /resources/ works with only required fields."""
        response = await integration_client.post(
            "/resources/",
            json={
                "source": "gem",
                "source_pk": "GEM-MIN-001",
                "data": {
                    "source": "gem",
                    "id": 400,
                    "name": "Minimal GEM Field",
                    "lat": 30.0,
                    "lon": -90.0,
                    "country": "USA",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] > 0
        assert data["name"] is None
        assert data["country"] is None
