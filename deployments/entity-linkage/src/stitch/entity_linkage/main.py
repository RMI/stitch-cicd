from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE
from .middleware import register_middlewares
from .auth import validate_auth_config_at_startup
from .settings import get_settings

from .routers.health import router as health_router

base_router = APIRouter(prefix="/api/v1")
base_router.include_router(health_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_auth_config_at_startup()
    yield


app = FastAPI(lifespan=lifespan)

settings = get_settings()

register_middlewares(application=app, settings=settings)

app.include_router(base_router)
