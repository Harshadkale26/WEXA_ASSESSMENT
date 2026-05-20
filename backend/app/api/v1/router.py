from fastapi import APIRouter

from app.api.v1.routers import analytics, auth, dashboards, health, ingestion

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, prefix="/health", tags=["health"])
api_v1_router.include_router(auth.router)
api_v1_router.include_router(ingestion.router)
api_v1_router.include_router(analytics.router)
api_v1_router.include_router(dashboards.router)
api_v1_router.include_router(dashboards.widgets_router)
