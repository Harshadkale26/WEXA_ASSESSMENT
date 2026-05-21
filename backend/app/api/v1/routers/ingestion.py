from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.ingestion import IngestionContext, get_ingestion_context
from app.core.config import settings
from app.core.webhook_signature import verify_webhook_signature
from app.dependencies import get_db, get_redis
from app.schemas.events import (
    BatchIngestionResponse,
    CsvIngestionResponse,
    EventAcceptedOut,
    IngestionBatchIn,
    IngestionEventIn,
    WebhookIngestionPayload,
)
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


def _ingestion_service(
    session: AsyncSession,
    redis: Redis,
    ctx: IngestionContext,
) -> IngestionService:
    return IngestionService(
        session,
        redis,
        organization_id=ctx.organization_id,
        api_key_row=ctx.api_key,
    )


@router.post("/events", response_model=EventAcceptedOut, status_code=status.HTTP_202_ACCEPTED)
async def ingest_single_event(
    payload: IngestionEventIn,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ctx: IngestionContext = Depends(get_ingestion_context),
) -> EventAcceptedOut:
    service = _ingestion_service(session, redis, ctx)
    return await service.ingest_single(payload)


@router.post("/events/batch", response_model=BatchIngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_batch_events(
    payload: IngestionBatchIn,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ctx: IngestionContext = Depends(get_ingestion_context),
) -> BatchIngestionResponse:
    service = _ingestion_service(session, redis, ctx)
    return await service.ingest_batch(payload)


@router.post("/events/csv", response_model=CsvIngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_events_csv(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ctx: IngestionContext = Depends(get_ingestion_context),
    file: UploadFile = File(..., description="CSV with columns: event_name,event_type,timestamp,source,payload"),
) -> CsvIngestionResponse:
    service = _ingestion_service(session, redis, ctx)
    return await service.ingest_csv(file)


@router.post("/webhooks/events", response_model=BatchIngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_webhook_events(
    request: Request,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    ctx: IngestionContext = Depends(get_ingestion_context),
) -> BatchIngestionResponse:
    """
    Webhook receiver for external systems.

    - Auth: `X-API-Key` (same as other ingestion routes)
    - Optional: `X-Webhook-Signature: sha256=<hmac>` of raw body using the key's webhook signing secret
    - Body: single event fields or `{ "events": [ ... ] }`
    """
    body = await request.body()
    secret = ctx.api_key.webhook_signing_secret
    signature = request.headers.get("X-Webhook-Signature")

    if settings.ingestion_webhook_signature_required:
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key has no webhook signing secret",
            )
        if not verify_webhook_signature(body, secret, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid X-Webhook-Signature",
            )
    elif secret and signature and not verify_webhook_signature(body, secret, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-Webhook-Signature",
        )

    payload = WebhookIngestionPayload.model_validate_json(body)
    batch = payload.to_batch()
    service = _ingestion_service(session, redis, ctx)
    return await service.ingest_webhook_batch(batch)
