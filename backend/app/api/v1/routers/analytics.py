from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.dependencies import get_db
from app.models.auth import User
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsQueryResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/query", response_model=AnalyticsQueryResponse)
async def run_analytics_query(
    payload: AnalyticsQueryRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalyticsQueryResponse:
    """
    Execute a dynamic analytics query over ingested events.

    Example body:
    ```json
    {
      "metric": "page_views",
      "aggregation": "count",
      "group_by": "hour",
      "time_range": "24h"
    }
    ```
    """
    return await AnalyticsService(session).query(current_user, payload)
