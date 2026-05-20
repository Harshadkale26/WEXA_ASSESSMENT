from fastapi import APIRouter, Depends, File, UploadFile, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.ingestion import IngestionContext, get_ingestion_context
from app.dependencies import get_db, get_redis
from app.schemas.events import (
    BatchIngestionResponse,
    CsvIngestionResponse,
    EventAcceptedOut,
    IngestionBatchIn,
    IngestionEventIn,
)
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/events", response_model=EventAcceptedOut, status_code=status.HTTP_202_ACCEPTED)
async def ingest_single_event(
    payload: IngestionEventIn,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ctx: IngestionContext = Depends(get_ingestion_context),
) -> EventAcceptedOut:
    service = IngestionService(
        session,
        redis,
        organization_id=ctx.organization_id,
        api_key_row=ctx.api_key,
    )
    return await service.ingest_single(payload)


@router.post("/events/batch", response_model=BatchIngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_batch_events(
    payload: IngestionBatchIn,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ctx: IngestionContext = Depends(get_ingestion_context),
) -> BatchIngestionResponse:
    service = IngestionService(
        session,
        redis,
        organization_id=ctx.organization_id,
        api_key_row=ctx.api_key,
    )
    return await service.ingest_batch(payload)


@router.post("/events/csv", response_model=CsvIngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_events_csv(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ctx: IngestionContext = Depends(get_ingestion_context),
    file: UploadFile = File(..., description="CSV with columns: event_name,event_type,timestamp,source,payload"),
) -> CsvIngestionResponse:
    service = IngestionService(
        session,
        redis,
        organization_id=ctx.organization_id,
        api_key_row=ctx.api_key,
    )
    return await service.ingest_csv(file)
