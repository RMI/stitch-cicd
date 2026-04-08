from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK


router = APIRouter()


@router.get("/health")
async def check_health():
    return JSONResponse(
        {"service": "entity_linkage", "status": "ok"}, status_code=HTTP_200_OK
    )
