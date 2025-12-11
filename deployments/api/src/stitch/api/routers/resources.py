from collections.abc import Sequence
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(
    prefix="/resources",
    responses={404: {"description": "Not found"}},
)


class ResourceBase(BaseModel):
    name: str | None
    country: str | None


class Resource(ResourceBase):
    id: int


_resources: list[Resource] = []


@router.get("/")
async def get_all_resources() -> Sequence[Resource]:
    return [r for r in _resources]


@router.get("/{id}", response_model=Resource)
async def get_resource(id: int) -> Resource:
    for r in _resources:
        if r.id == id:
            return r
    raise HTTPException(status_code=404, detail=f"Resource (id: {id}) not found")


@router.post("/", response_model=Resource)
async def create_resource(*, resource_in: ResourceBase) -> Resource:
    id_ = len(_resources) + 1
    res = Resource(id=id_, name=resource_in.name, country=resource_in.country)
    _resources.append(res)
    return res
