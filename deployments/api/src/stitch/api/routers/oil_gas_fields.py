import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from stitch.api.entities import PaginatedResponse, PaginationParams

from stitch.api.db import og_field_resource_actions as resource_actions
from stitch.api.db.config import UnitOfWorkDep
from stitch.api.auth import CurrentUser
from stitch.api.db.utils import (
    resource_to_view,
    resource_to_list_item_view,
    resource_to_detail_view,
)

from stitch.ogsi.model import (
    OGFieldDetailView,
    OGFieldListItemView,
    OGFieldResource,
    OGFieldView,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/oil-gas-fields",
    tags=["oil_gas_fields"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_resources(
    *, uow: UnitOfWorkDep, user: CurrentUser, pagination: Annotated[PaginationParams, Query()]
) -> PaginatedResponse[OGFieldListItemView]:
    resources, total_count = await resource_actions.query(
        session=uow.session, page=pagination.page, page_size=pagination.page_size
    )
    return PaginatedResponse(
        items=[resource_to_list_item_view(r) for r in resources],
        total_count=total_count,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{id}", response_model=OGFieldView)
async def get_resource(
    *, uow: UnitOfWorkDep, user: CurrentUser, id: int
) -> OGFieldView:
    res: OGFieldResource = await resource_actions.get(session=uow.session, id=id)
    return resource_to_view(resource=res)


@router.get("/{id}/detail", response_model=OGFieldDetailView)
async def get_resource_detail(
    *, uow: UnitOfWorkDep, user: CurrentUser, id: int
) -> OGFieldDetailView:
    res: OGFieldResource = await resource_actions.get(session=uow.session, id=id)
    return resource_to_detail_view(resource=res)


@router.post("/", response_model=OGFieldResource)
async def create_resource(
    *, uow: UnitOfWorkDep, user: CurrentUser, resource_in: OGFieldResource
) -> OGFieldResource:
    return await resource_actions.create(
        session=uow.session, user=user, resource=resource_in
    )


@router.post("/merge", response_model=OGFieldResource)
async def merge_resources_endpoint(
    *, uow: UnitOfWorkDep, user: CurrentUser, resource_ids: list[int]
) -> OGFieldResource:
    """
    Merge multiple resources into one (STUB):
    repoint resource_ids[1:] -> resource_ids[0]
    """
    # preserve order but drop duplicates
    unique_ids = list(dict.fromkeys(resource_ids))
    if len(unique_ids) < 2:
        raise HTTPException(
            status_code=400, detail="Provide at least 2 unique resource IDs"
        )

    logger.info(
        "Merge requested by user=%s for resource_ids=%s",
        getattr(user, "sub", "<anon>"),
        unique_ids,
    )

    try:
        return await resource_actions.merge_resources(
            session=uow.session,
            user=user,
            resource_ids=unique_ids,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error while merging resources %s: %s", unique_ids, exc)
        raise HTTPException(status_code=500, detail="Internal error during merge")
