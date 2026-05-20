"""Repository abstraction for analytics query execution."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsQueryResponse
from app.services.analytics.query_engine import AnalyticsQueryEngine


class AnalyticsRepository:
    """
    Data-access layer for event analytics.
    Delegates to AnalyticsQueryEngine for safe dynamic SQL generation.
    """

    def __init__(self, session: AsyncSession, organization_id: UUID) -> None:
        self.session = session
        self.organization_id = organization_id
        self._engine = AnalyticsQueryEngine(session, organization_id)

    async def run_query(self, request: AnalyticsQueryRequest) -> AnalyticsQueryResponse:
        return await self._engine.execute(request)

    async def run_scalar(self, request: AnalyticsQueryRequest) -> float:
        """Single aggregate value (no group_by)."""
        req = request.model_copy(update={"group_by": None, "page": 1, "page_size": 1})
        result = await self._engine.execute(req)
        return result.data[0].value if result.data else 0.0
