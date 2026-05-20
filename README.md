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

## Migrations

```bash
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head
```
