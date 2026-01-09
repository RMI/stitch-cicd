from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND
from stitch.api.db.model import ResourceModel
from stitch.api.db.sources import get_sources_from_memberships
from stitch.api.deps import CurrentUser
from stitch.api.entities import CreateResource, Resource


async def resource_model_to_entity(
    session: AsyncSession, model: ResourceModel
) -> Resource:
    source_models = await get_sources_from_memberships(session, model.memberships)
    source_data = dict([(k, src.to_entity()) for k, src in source_models.items()])
    return Resource(
        id=model.id,
        name=model.name,
        country=model.country,
        source_data=source_data,
        constituents=[],
        created=model.created,
        updated=model.updated,
    )


async def get(session: AsyncSession, id: int):
    model = await session.get(ResourceModel, id)
    if model is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"No Resource with id `{id}` found."
        )
    await session.refresh(model, ["memberships"])
    return await resource_model_to_entity(session, model)


async def create(session: AsyncSession, user: CurrentUser, resource: CreateResource):
    model = ResourceModel.create(
        created_by=user, name=resource.name, country=resource.country
    )
    session.add(model)
    await session.flush()
    await session.refresh(model, ["memberships"])
    return await resource_model_to_entity(session, model)
