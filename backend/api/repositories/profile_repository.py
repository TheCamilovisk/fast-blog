from sqlalchemy import select

from api.models.profile import Profile
from api.repositories.base_repository import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    model = Profile

    @classmethod
    def list(  # noqa: PLR0913, PLR0917
        cls,
        session,
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

        query = query.limit(limit).offset(offset)
        return session.scalars(query).all()
