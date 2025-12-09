from fastapi import APIRouter, FastAPI

from .routers.resources import router as resource_router

base_router = APIRouter(prefix="/api/v1")
base_router.include_router(resource_router)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from Stitch API!"}
