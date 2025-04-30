from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.database import table_registry


@table_registry.mapped_as_dataclass
class Post:
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(
        Boolean, init=False, default=False
    )

    created_at: Mapped[str] = mapped_column(
        DateTime, init=False, default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime, init=False, default=func.now(), onupdate=func.now()
    )
    published_at: Mapped[str] = mapped_column(
        DateTime, init=False, default=None, nullable=True
    )

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('profiles.id'), nullable=False
    )

    author = relationship('Profile', back_populates='posts', lazy='selectin')

    tags: Mapped[list['Tag']] = relationship(  # noqa: F821 # type: ignore
        'Tag',
        init=False,
        secondary='posts_tags',
        back_populates='posts',
        lazy='selectin',
        join_depth=2,
    )
