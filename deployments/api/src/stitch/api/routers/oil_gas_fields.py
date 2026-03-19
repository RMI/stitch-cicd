from fastapi import APIRouter

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

router = APIRouter(
    prefix="/oil-gas-fields",
    tags=["oil_gas_fields"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[OGFieldListItemView])
async def get_all_resources(
    *, uow: UnitOfWorkDep, user: CurrentUser
) -> list[OGFieldListItemView]:
    resources = list(await resource_actions.get_all(session=uow.session))
    return [resource_to_list_item_view(r) for r in resources]


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
