from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.status import HTTP_502_BAD_GATEWAY

from stitch.entity_linkage.auth import AuthContext
from stitch.entity_linkage.client import StitchApiClient
from stitch.entity_linkage.entities import User
from stitch.entity_linkage.errors import StitchAPIError

router = APIRouter(tags=["entity-linkage"])


class StartRequest(BaseModel):
    apply_merges: bool = Field(
        default=False,
        description=(
            "When true, later linkage runs may POST confirmed match groups to "
            "the Stitch API. Ignored in this first stub."
        ),
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


class StartResponse(BaseModel):
    initiated_by: str
    apply_merges: bool
    relay_mode: str
    downstream_preview_count: int
    downstream_payload: dict[str, Any] | list[dict[str, Any]]


def _extract_user_label(user: User) -> str:
    return user.name or user.email or user.sub


def _preview_count(payload: dict[str, Any] | list[dict[str, Any]]) -> int:
    if isinstance(payload, list):
        return len(payload)

    items = payload.get("items")
    if isinstance(items, list):
        return len(items)

    return 0


@router.post("/start", response_model=StartResponse)
async def start(
    request: StartRequest,
    auth_context: AuthContext,
) -> StartResponse:
    """
    Minimal transparent-relay stub.

    TODO:
    - persist fetched rows locally
    - run exact-name matching
    - call details endpoints for second-phase checks
    - apply merges when apply_merges=true
    """
    try:
        async with StitchApiClient(auth_context=auth_context) as client:
            downstream_payload = await client.list_oil_gas_fields(
                page=request.page,
                page_size=request.page_size,
            )
    except StitchAPIError as exc:
        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return StartResponse(
        initiated_by=_extract_user_label(auth_context.user),
        apply_merges=request.apply_merges,
        relay_mode="transparent",
        downstream_preview_count=_preview_count(downstream_payload),
        downstream_payload=downstream_payload,
    )
