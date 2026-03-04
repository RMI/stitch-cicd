import asyncio
from collections.abc import Sequence
from functools import partial
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND
from stitch.api.resources.entities import CreateResource, Resource
from stitch.api.auth import CurrentUser

from .model import (
    ResourceModel,
)


async def resource_model_to_entity(
    session: AsyncSession, model: ResourceModel
) -> Resource:
    # Domain-agnostic: constituents are just ids, and there is no source_data.
    constituent_models = await ResourceModel.get_constituents_by_root_id(
        session, model.id
    )
    constituent_ids = [m.id for m in constituent_models if m.id != model.id]
    return Resource(
        id=model.id,
        name=model.name,
        repointed_to=model.repointed_id,
        constituents=constituent_ids,
        created=str(model.created) if getattr(model, "created", None) else None,
        updated=str(model.updated) if getattr(model, "updated", None) else None,
    )


async def get_all(session: AsyncSession) -> Sequence[Resource]:
    stmt = select(ResourceModel).where(ResourceModel.repointed_id.is_(None))
    models = (await session.scalars(stmt)).all()
    fn = partial(resource_model_to_entity, session)
    return await asyncio.gather(*[fn(m) for m in models])


async def get(session: AsyncSession, id: int):
    model = await session.get(ResourceModel, id)
    if model is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"No Resource with id `{id}` found."
        )
    return await resource_model_to_entity(session, model)


async def create(session: AsyncSession, user: CurrentUser, resource: CreateResource):
    """
    Domain-agnostic create:
    - create the resource row only
    """
    model = ResourceModel.create(
        created_by=user,
        name=resource.name,
    )
    session.add(model)
    await session.flush()
    return await resource_model_to_entity(session, model)
