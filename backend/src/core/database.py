from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    future=True,
    echo=False if settings.environment == 'production' else True,
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes.
    """
    async with AsyncSessionLocal() as session:
        yield session
