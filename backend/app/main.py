from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import Response

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.routers import health, mpk

_frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

app = FastAPI(
    title="New Salt City Bus",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(mpk.router)


@app.on_event("startup")
async def startup():
    logger.info("Application starting", extra={"env": settings.app_env})


# Serve frontend static files if the build exists
if _frontend_dist.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="assets")

    _index_html = (_frontend_dist / "index.html").read_bytes()

    @app.middleware("http")
    async def spa_middleware(request: Request, call_next):
        response = await call_next(request)
        # If FastAPI returned 404 and it's not an /api/ route, serve index.html
        if response.status_code == 404 and not request.url.path.startswith("/api/"):
            return Response(content=_index_html, media_type="text/html")
        return response
