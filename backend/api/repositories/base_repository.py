from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseRepository(Generic[T]):
    model: Type[T]

    @classmethod
    async def get_by_id(cls, session: AsyncSession, obj_id: int) -> T | None:
        return await session.scalar(
            select(cls.model).filter(cls.model.id == obj_id)
        )

    @classmethod
    async def list_all(
        cls, session: AsyncSession, limit: int = 10, offset: int = 0
    ) -> list[T]:
        return await session.scalars(
            select(cls.model).offset(offset).limit(limit)
        ).all()

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> T:
        obj = cls.model(**kwargs)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    @classmethod
    async def update(cls, session: AsyncSession, obj: T, **kwargs) -> T:
        for key, value in kwargs.items():
            if value is not None:
                setattr(obj, key, value)
        await session.commit()
        await session.refresh(obj)
        return obj

    @classmethod
    async def delete(cls, session: AsyncSession, obj: T) -> None:
        await session.delete(obj)
        await session.commit()
