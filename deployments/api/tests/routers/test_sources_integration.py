"""Integration tests for oil-gas-field-sources router."""

import pytest
from httpx import AsyncClient

from tests.factories import ResourceCreateFactory


class TestQuerySourcesIntegration:
    """Integration tests for GET /oil-gas-field-sources/ paginated endpoint."""

    @pytest.mark.anyio
    async def test_list_returns_paginated_envelope(
        self,
        integration_client: AsyncClient,
        og_create_res_fact: ResourceCreateFactory,
    ):
        # Create resources (which create sources + memberships)
        for name in ["A", "B", "C"]:
            await integration_client.post(
                "/oil-gas-fields/",
                json=og_create_res_fact(name=name).model_dump(mode="json"),
            )

        response = await integration_client.get("/oil-gas-field-sources/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_count" in data
        assert data["page"] == 1
        assert data["page_size"] == 50
        assert data["total_count"] > 0
        assert len(data["items"]) == data["total_count"]

    @pytest.mark.anyio
    async def test_default_params_return_results(
        self,
        integration_client: AsyncClient,
    ):
        response = await integration_client.get("/oil-gas-field-sources/")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 50
