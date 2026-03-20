from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.routers import health, mpk

app = FastAPI(
    title="GFT Platform",
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


# In production, serve frontend static files
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
