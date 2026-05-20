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

2. Start all services:

   ```bash
   docker compose up --build
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

1. Run migrations (includes `events` + `organization_api_keys`).
2. Create an API key (JWT, Admin+): `POST /api/v1/auth/api-keys`
3. Ingest with header `X-API-Key: <plaintext key>`:

   - `POST /api/v1/ingestion/events` — single event (JSON)
   - `POST /api/v1/ingestion/events/batch` — batch (JSON)
   - `POST /api/v1/ingestion/events/csv` — CSV upload (`event_name,event_type,timestamp,source,payload`)

Rate limits and batch limits are configurable via `INGESTION_*` environment variables.

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
