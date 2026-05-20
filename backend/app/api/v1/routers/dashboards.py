from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user, require_minimum_role
from app.dependencies import get_db
from app.models.auth import Role, User
from app.schemas.dashboard import (
    DashboardCreate,
    DashboardDetailResponse,
    DashboardResponse,
    DashboardUpdate,
    WidgetCreate,
    WidgetDataQueryOverride,
    WidgetDataResponse,
    WidgetResponse,
    WidgetUpdate,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("", response_model=list[DashboardResponse])
async def list_dashboards(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DashboardResponse]:
    return await DashboardService(session).list_dashboards(current_user)


@router.post("", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    payload: DashboardCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_minimum_role(Role.ANALYST)),
) -> DashboardResponse:
    return await DashboardService(session).create_dashboard(current_user, payload)


@router.get("/{dashboard_id}", response_model=DashboardDetailResponse)
async def get_dashboard(
    dashboard_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardDetailResponse:
    return await DashboardService(session).get_dashboard(current_user, dashboard_id)


@router.patch("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: UUID,
    payload: DashboardUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_minimum_role(Role.ANALYST)),
) -> DashboardResponse:
    return await DashboardService(session).update_dashboard(current_user, dashboard_id, payload)


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_minimum_role(Role.ADMIN)),
) -> None:
    await DashboardService(session).delete_dashboard(current_user, dashboard_id)


# --- Widgets (nested under dashboard) ---


@router.get("/{dashboard_id}/widgets", response_model=list[WidgetResponse])
async def list_widgets(
    dashboard_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WidgetResponse]:
    return await DashboardService(session).list_widgets(current_user, dashboard_id)


@router.post(
    "/{dashboard_id}/widgets",
    response_model=WidgetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_widget(
    dashboard_id: UUID,
    payload: WidgetCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_minimum_role(Role.ANALYST)),
) -> WidgetResponse:
    return await DashboardService(session).create_widget(current_user, dashboard_id, payload)


# --- Widget by id (org-scoped) ---

widgets_router = APIRouter(prefix="/widgets", tags=["widgets"])


@widgets_router.get("/{widget_id}", response_model=WidgetResponse)
async def get_widget(
    widget_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WidgetResponse:
    return await DashboardService(session).get_widget(current_user, widget_id)


@widgets_router.patch("/{widget_id}", response_model=WidgetResponse)
async def update_widget(
    widget_id: UUID,
    payload: WidgetUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_minimum_role(Role.ANALYST)),
) -> WidgetResponse:
    return await DashboardService(session).update_widget(current_user, widget_id, payload)


@widgets_router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_minimum_role(Role.ANALYST)),
) -> None:
    await DashboardService(session).delete_widget(current_user, widget_id)


@widgets_router.post("/{widget_id}/data", response_model=WidgetDataResponse)
async def query_widget_data(
    widget_id: UUID,
    override: WidgetDataQueryOverride | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WidgetDataResponse:
    """Execute widget analytics query (aggregation + filters + time range)."""
    return await DashboardService(session).get_widget_data(current_user, widget_id, override)
