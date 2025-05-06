from typing import Tuple

from sqlalchemy import or_, select
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
    ) -> Tuple[int, list[User]]:
        query = select(cls.model)

        if username:
            query = query.filter(cls.model.username.ilike(f'%{username}%'))

        if email:
            query = query.filter(cls.model.email.ilike(f'%{email}%'))

        total = await cls.count_query(session, query)

        query = await session.scalars(
            query.order_by(cls.model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return total, query.all()

    @classmethod
    async def find_by_id_or_email(
        cls, session: AsyncSession, identifier: str
    ) -> User | None:
        query = await session.scalar(
            select(User).filter(
                or_(User.username == identifier, User.email == identifier)
            )
        )

        return query
