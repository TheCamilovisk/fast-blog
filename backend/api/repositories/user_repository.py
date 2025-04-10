from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.user import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    @classmethod
    def find_by_username(cls, session: Session, username: str) -> User | None:
        return session.scalar(
            select(User).filter(User.username.ilike(f'%{username}%'))
        )

    @classmethod
    def find_by_email(cls, session: Session, email: str) -> User | None:
        return session.scalar(
            select(User).filter(User.email.ilike(f'%{email}%'))
        )
