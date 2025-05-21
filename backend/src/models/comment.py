from __future__ import annotations

from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models._table_registry import table_registry

from ._mixins import TimestampMixin


@table_registry.mapped_as_dataclass
class Comment(TimestampMixin):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    author: Mapped['User'] = relationship(  # noqa: F821 # type: ignore
        'User', init=False, back_populates='comments', lazy='selectin'
    )

    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('posts.id'), nullable=False
    )
    post: Mapped['Post'] = relationship(  # noqa: F821 # type: ignore
        'Post', init=False, back_populates='comments', lazy='selectin'
    )

    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('comments.id'), init=False
    )
    parent: Mapped[Optional[Comment]] = relationship(
        back_populates='replies',
        remote_side=[id],
        lazy='selectin',
    )
    replies: Mapped[List[Comment]] = relationship(
        back_populates='parent',
        cascade='all, delete-orphan',
        lazy='selectin',
        init=False,
        join_depth=2,
    )

    @classmethod
    def create(
        cls,
        content: str,
        post_id: int,
        author_id: int,
        parent: Comment | None = None,
    ) -> Comment:
        return cls(
            content=content,
            post_id=post_id,
            author_id=author_id,
            parent=parent,
        )

    def update(self, content: str) -> None:
        self.content = content
