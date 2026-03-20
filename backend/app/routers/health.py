from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.api_route("/healthz", methods=["GET", "HEAD"])
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    return {"status": "ready"}
