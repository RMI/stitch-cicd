import logging

from collections.abc import Sequence

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field

from stitch.api.db import resource_actions
from stitch.api.db.config import UnitOfWorkDep
from stitch.api.auth import CurrentUser
from stitch.api.entities import CreateResource, Resource
# from stitch.core.resources.app.services.resource_service import merge_resources

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/resources",
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_resources(
    *, uow: UnitOfWorkDep, user: CurrentUser
) -> Sequence[Resource]:
    return await resource_actions.get_all(session=uow.session)


@router.get("/{id}", response_model=Resource)
async def get_resource(*, uow: UnitOfWorkDep, user: CurrentUser, id: int) -> Resource:
    return await resource_actions.get(session=uow.session, id=id)


@router.post("/", response_model=Resource)
async def create_resource(
    *, uow: UnitOfWorkDep, user: CurrentUser, resource_in: CreateResource
) -> Resource:
    return await resource_actions.create(
        session=uow.session, user=user, resource=resource_in
    )

class MergeRequest(BaseModel):
    resource_ids: list[int] = Field(..., items=2)

@router.post("/merge", response_model=Resource)
async def merge_resources_endpoint(
    *, uow: UnitOfWorkDep, user: CurrentUser, payload: MergeRequest
) -> Resource:
    """
    Merge multiple resources into one.
    Calls the core ResourceService.merge_resources(...) and returns the
    merged root id and canonical resource URL.
    """
    ids = payload.resource_ids
    # preserve order but drop duplicates
    unique_ids = list(dict.fromkeys(ids))
    if len(unique_ids) != 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 unique resource IDs")

    logger.info("Merge requested by user=%s for resource_ids=%s", getattr(user, "sub", "<anon>"), unique_ids)

    target_id = ids[0]
    try:

        # ---- STUB BEHAVIOR ----
        # TODO: Replace with real merge implementation
        merged_id = target_id

        logger.warning(
            "Stub merge executed. Returning target_id=%s as merged_id NO DATA ALTERED",
            merged_id,
        )
        # -----------------------

        return await resource_actions.get(session=uow.session, id=target_id)

    except Exception as exc:
        # You can make this narrower (catch ResourceIntegrityError, EntityNotFoundError, etc.)
        logger.exception("Error while merging resources %s: %s", unique_ids, exc)
        raise HTTPException(status_code=500, detail="Internal error during merge")
