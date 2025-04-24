from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import table_registry
from api.models.profile import Profile
from api.models.token import RefreshToken


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        'RefreshToken',
        init=False,
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, default=func.now(), onupdate=func.now()
    )
    superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Profile | None = relationship(
        'Profile',
        init=False,
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )
