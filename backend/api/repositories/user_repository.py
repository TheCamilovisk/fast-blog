from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.user import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    @classmethod
    def list_all(
        cls,
        session: Session,
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

        return session.scalars(query.offset(offset).limit(limit)).all()
