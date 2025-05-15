from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models._mixins import TimestampMixin
from src.models._table_registry import table_registry
from src.utils.security import hash_password, verify_password


@table_registry.mapped_as_dataclass
class User(TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, index=True
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(256), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    posts: Mapped[List['Post']] = relationship(  # type: ignore # noqa: F821
        'Post',
        back_populates='author',
        uselist=True,
        init=False,
        default=[],
        lazy='selectin',
    )

    @classmethod
    def create(cls, username: str, email: str, password: str) -> User:
        return cls(
            username=username,
            email=email,
            password=hash_password(password),
        )

    @staticmethod
    def hash_password(plain_password) -> str:
        return hash_password(plain_password)

    def verify_password(self, plain_password) -> bool:
        return verify_password(plain_password, self.password)

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def make_superuser(self) -> None:
        self.is_superuser = True

    def make_normaluser(self) -> None:
        self.is_superuser = False
