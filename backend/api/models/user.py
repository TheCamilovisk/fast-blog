from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, default=func.now(), onupdate=func.now()
    )
    superuser: Mapped[bool] = mapped_column(default=False)

    @classmethod
    def list(cls, session, limit: int = 10, offset: int = 0):
        return session.scalars(select(cls).offset(offset).limit(limit)).all()

    @classmethod
    def get_by_id(cls, session, user_id: int):
        return session.scalar(select(cls).filter(cls.id == user_id))

    @classmethod
    def create(cls, session, username: str, password: str, email: str):
        user = cls(username=username, password=password, email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @classmethod
    def update(
        cls,
        session,
        user: User,
        username: str = None,
        email: str = None,
    ):
        if user is None:
            return None

        if username:
            user.username = username
        if email:
            user.email = email

        session.commit()
        session.refresh(user)
        return user

    @classmethod
    def delete(cls, session, user: User):
        if user is None:
            return None

        session.delete(user)
        session.commit()
        return user

    @classmethod
    def update_password(
        cls,
        session,
        user: User,
        password: str,
    ):
        if user is None:
            return None

        user.password = password
        session.commit()
        session.refresh(user)
        return user

    @classmethod
    def get_by_username_or_email(cls, session, username_or_email: str):
        return session.scalar(
            select(cls).filter(
                (cls.username == username_or_email)
                | (cls.email == username_or_email)
            )
        )

    @classmethod
    def make_superuser(cls, session, user: User):
        if user is None:
            return None

        user.superuser = True
        session.commit()
        session.refresh(user)
        return user
