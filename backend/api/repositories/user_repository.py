from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.user import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    @classmethod
    def get_by_username(cls, session: Session, username: str) -> User | None:
        return session.scalar(select(User).filter(User == username))

    @classmethod
    def get_by_email(cls, session: Session, email: str) -> User | None:
        return session.scalar(select(User).filter(User.email == email))
