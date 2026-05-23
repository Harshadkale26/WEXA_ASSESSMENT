from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def create_engine() -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        echo=settings.is_development,
        pool_pre_ping=True,
    )


engine: AsyncEngine = create_engine()

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_redis_client() -> Redis:
    print("REDIS_URL",settings.redis_url)
    return Redis.from_url(str(settings.redis_url), decode_responses=True)


async def dispose_engine() -> None:
    await engine.dispose()

