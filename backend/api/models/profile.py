from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import table_registry
from api.models.post import Post


@table_registry.mapped_as_dataclass
class Profile:
    __tablename__ = 'profiles'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), unique=True, nullable=False
    )

    user = relationship('User', back_populates='profile', lazy='selectin')

    posts: Mapped[list[Post]] = relationship(
        'Post',
        init=False,
        back_populates='author',
        uselist=True,
        cascade='all, delete-orphan',
        lazy='selectin',
        join_depth=2,
    )
