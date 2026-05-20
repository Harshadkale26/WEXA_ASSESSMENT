from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_v1_router
from app.config import settings
from app.database import dispose_engine
from app.exceptions import setup_exception_handlers
from app.logging import get_logger
from app.middleware import setup_middleware

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("lifespan_start", app=settings.app_name, environment=settings.environment)
    yield
    await dispose_engine()
    log.info("lifespan_stop", app=settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    setup_middleware(app)
    setup_exception_handlers(app)

    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
