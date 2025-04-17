from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    @classmethod
    async def list_all(
        cls,
        session: AsyncSession,
        username: str | None = None,
        email: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[User]:
        query = select(cls.model)

        if username:
            query = query.filter(cls.model.username.ilike(f'%{username}%'))

        if email:
            query = query.filter(cls.model.email.ilike(f'%{email}%'))

        query = await session.scalars(query.offset(offset).limit(limit))

        return query.all()
