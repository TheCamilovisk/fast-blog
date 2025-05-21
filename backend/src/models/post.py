from __future__ import annotations

from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models._mixins import TimestampMixin
from src.models._table_registry import table_registry


def _slugfy(title: str) -> str:
    base = title.lower().replace(' ', '-')
    suffix = uuid4().hex[:8]
    return f'{base}-{suffix}'


@table_registry.mapped_as_dataclass
class Post(TimestampMixin):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(300), unique=True, nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    author: Mapped['User'] = relationship(  # type: ignore # noqa: F821
        'User', init=False, back_populates='posts', lazy='selectin'
    )

    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    comments: Mapped[List['Comment']] = relationship(  # noqa: F821 # type: ignore
        'Comment',
        back_populates='post',
        uselist=True,
        init=False,
        default=[],
        lazy='selectin',
    )

    @classmethod
    def create(
        cls, title: str, subtitle: str, content: str, author_id: int
    ) -> Post:
        slug = _slugfy(title=title)
        return cls(
            title=title,
            subtitle=subtitle,
            slug=slug,
            content=content,
            author_id=author_id,
        )

    def update(
        self,
        title: str | None = None,
        subtitle: str | None = None,
        content: str | None = None,
    ) -> None:
        if self.title != title:
            self.title = title
            self.slug = _slugfy(title=title)
        if subtitle:
            self.subtitle = subtitle
        if content:
            self.content = content

    def publish(self):
        if self.is_published:
            return
        self.is_published = True
        self.published_at = datetime.now(timezone.utc)

    def unpublish(self):
        self.is_published = False
        self.published_at = None
