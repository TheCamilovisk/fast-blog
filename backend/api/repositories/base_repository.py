from typing import Generic, Tuple, Type, TypeVar

from sqlalchemy import Select, func, select
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
    async def count_query(cls, session: AsyncSession, query: Select[Tuple[T]]):
        count = select(func.count()).select_from(query.subquery())
        count_result = await session.execute(count)
        return count_result.scalar_one()

    @classmethod
    async def list_all(
        cls, session: AsyncSession, limit: int = 10, offset: int = 0
    ) -> Tuple[int, list[T]]:
        query = (
            select(cls.model)
            .order_by(cls.model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        total = await cls.count_query(query)

        query = await session.scalars(session, query)

        return total, query.all()

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
