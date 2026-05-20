from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import Event, EventProcessingStatus


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, event_id: UUID, *, organization_id: UUID) -> Event | None:
        stmt = select(Event).where(Event.id == event_id, Event.organization_id == organization_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_worker(self, event_id: UUID) -> Event | None:
        return await self.session.get(Event, event_id)

    async def add(self, event: Event) -> Event:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def add_many(self, events: list[Event]) -> None:
        self.session.add_all(events)
        await self.session.flush()

    async def refresh(self, event: Event) -> None:
        await self.session.refresh(event)
