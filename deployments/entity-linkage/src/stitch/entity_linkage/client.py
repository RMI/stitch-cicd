from __future__ import annotations

from typing import Any

import httpx

from stitch.entity_linkage.entities import RequestAuthContext
from stitch.entity_linkage.errors import StitchAPIError
from stitch.entity_linkage.settings import get_settings


def _get_api_base_url() -> str:
    """
    Resolve the downstream Stitch API base URL.

    TODO:
    - standardize the exact setting name once the deployment contract settles
    """
    settings = get_settings()
    return (
        getattr(settings, "stitch_api_base_url", None)
        or getattr(settings, "api_base_url", None)
        or "http://api:8000/api/v1"
    )


class StitchApiClient:
    def __init__(self, auth_context: RequestAuthContext):
        self._auth_context = auth_context
        self._client = httpx.AsyncClient(
            base_url=_get_api_base_url(),
            timeout=30.0,
        )

    async def __aenter__(self) -> "StitchApiClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._auth_context.bearer_token:
            headers["Authorization"] = f"Bearer {self._auth_context.bearer_token}"

        # TODO:
        # - add provenance headers separately from auth
        # - e.g. initiated-by user metadata
        # - replace transparent relay with machine/OBO auth later
        return headers

    async def list_oil_gas_fields(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        response = await self._client.get(
            "/oil-gas-fields/",
            params={"page": page, "page_size": page_size},
            headers=self._headers(),
        )
        self._raise_for_status(response, "GET /oil-gas-fields/")
        return response.json()

    async def post_merge(
        self,
        *,
        resource_ids: list[str] | list[int],
    ) -> dict[str, Any] | list[dict[str, Any]]:
        response = await self._client.post(
            "/oil-gas-fields/merge",
            json={"resource_ids": resource_ids},
            headers=self._headers(),
        )
        self._raise_for_status(response, "POST /oil-gas-fields/merge")
        return response.json()

    @staticmethod
    def _raise_for_status(response: httpx.Response, operation: str) -> None:
        if response.is_success:
            return
        raise StitchAPIError(
            f"{operation} failed with status {response.status_code}: {response.text}"
        )
