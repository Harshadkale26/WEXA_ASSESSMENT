import logging

from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """Base service with shared session and logger."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.logger = logging.getLogger(self.__class__.__module__)
