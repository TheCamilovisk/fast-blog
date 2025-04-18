from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.profile import Profile
from api.repositories.base_repository import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    model = Profile

    @classmethod
    async def list_all(  # noqa: PLR0913, PLR0917
        cls,
        session: AsyncSession,
        firstname: str | None = None,
        lastname: str | None = None,
        username: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Profile]:
        query = select(cls.model)

        if firstname:
            query = query.where(cls.model.firstname == firstname)
        if lastname:
            query = query.where(cls.model.lastname == lastname)
        if username:
            query = query.where(cls.model.username == username)

        query = await session.scalars(query.limit(limit).offset(offset))
        return query.all()

    @classmethod
    async def get_by_user_id(
        cls, session: AsyncSession, user_id: int
    ) -> Profile | None:
        query = select(cls.model).where(cls.model.user_id == user_id)
        return await session.scalar(query)
