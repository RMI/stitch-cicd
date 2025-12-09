from collections.abc import Sequence
from typing import Annotated
from fastapi import APIRouter, Depends

from stitch.core.resources.app.services.resource_service import ResourceService
from stitch.core.resources.domain.entities import AggregateResourceEntity

from stitch.api.dependencies import get_resource_service

router = APIRouter(
    prefix="/resources",
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_resources(
    res_svc: Annotated[ResourceService, Depends(get_resource_service)],
) -> Sequence[AggregateResourceEntity]:
    return list(res_svc.get_all_resources())
