from fastapi import APIRouter

from app.api.v1.routers import health

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, prefix="/health", tags=["health"])
