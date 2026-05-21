# Real-Time Analytics SaaS Platform

Production-grade monorepo for a real-time analytics SaaS platform.

## Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Backend  | FastAPI, SQLAlchemy (async), PostgreSQL, Redis  |
| Workers  | Celery                                          |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind   |
| Infra    | Docker Compose                                  |

## Project structure

```
.
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── docker-compose.yml
└── .env.example
```

## Quick start

1. Copy environment files:

   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```

2. Start all services (migrations run automatically on backend/worker startup):

   ```bash
   docker compose up --build
   ```

   Or apply migrations manually after the stack is up:

   ```bash
   docker compose exec backend alembic upgrade head
   ```

3. Access:

   - API: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Frontend: http://localhost:3000

## Backend architecture

Clean architecture layers under `backend/app/`:

- `api/v1/routers/` — HTTP route handlers
- `services/` — application / use-case logic
- `repositories/` — data access
- `models/` — SQLAlchemy ORM models
- `schemas/` — Pydantic request/response models
- `core/` — config, logging, dependencies
- `db/` — database session and base
- `celery_app/` — async task workers

## Event ingestion (API key)

1. Run migrations (`docker compose exec backend alembic upgrade head`).
2. Create an API key (JWT owner/admin, or **Settings** in the UI): `POST /api/v1/auth/api-keys`
3. Manage keys: `GET /api/v1/auth/api-keys`, `POST .../revoke`, `POST .../rotate`
4. Ingest with header `X-API-Key: <plaintext key>`:

   | Endpoint | Source type |
   |----------|-------------|
   | `POST /api/v1/ingestion/events` | Single JSON event |
   | `POST /api/v1/ingestion/events/batch` | Batch JSON |
   | `POST /api/v1/ingestion/events/csv` | CSV upload |
   | `POST /api/v1/ingestion/webhooks/events` | Webhook receiver (optional `X-Webhook-Signature`) |

- **Validation:** Pydantic models (`IngestionEventIn`, `WebhookIngestionPayload`, …)
- **Processing:** Celery task `events.process_event` → normalization → `normalized_payload` in PostgreSQL (indexed by org + timestamp)
- **Rate limits:** per organization (`INGESTION_RATE_LIMIT_PER_MINUTE`) and per API key (`INGESTION_RATE_LIMIT_PER_KEY_PER_MINUTE`)
- **Webhooks:** HMAC-SHA256 of raw body with signing secret returned on key create/rotate (`INGESTION_WEBHOOK_SIGNATURE_REQUIRED=true` to enforce)

## Frontend (Next.js 14)

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Stack: App Router, TypeScript, Tailwind, Zustand (auth), TanStack Query, Axios.

| Path | Description |
|------|-------------|
| `/login`, `/signup` | Auth (public) |
| `/dashboard` | Overview (protected) |
| `/analytics`, `/dashboards`, `/ingestion`, `/settings` | App sections |

Protected routes use middleware (`access_token` cookie) + client `AuthGuard`.

## Celery (Redis broker)

| Service | Command |
|---------|---------|
| Worker | `celery -A app.celery_app.celery_app worker -Q analytics.default,analytics.ingestion,analytics.priority` |
| Beat | `celery -A app.celery_app.celery_app beat` |

Health endpoints:
- `GET /api/v1/health` — includes Celery worker ping status
- `GET /api/v1/health/celery` — registered tasks + worker detail

Ingestion events are processed by `events.process_event` on queue `analytics.ingestion` with exponential backoff retries.

## Migrations

```bash
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head
```
