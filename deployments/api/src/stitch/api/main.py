from fastapi import APIRouter, FastAPI

from .routers.resources import router as resource_router
from .routers.health import router as health_router

base_router = APIRouter(prefix="/api/v1")
base_router.include_router(resource_router)
base_router.include_router(health_router)

app = FastAPI()


@base_router.get("/")
async def root():
    return {"message": "Hello from Stitch API!"}


app.include_router(base_router)
