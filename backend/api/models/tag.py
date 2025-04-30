from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.database import table_registry
from api.models.posts_tags import posts_tags  # noqa: F401


@table_registry.mapped_as_dataclass
class Tag:
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, default=func.now(), onupdate=func.now()
    )

    posts: Mapped[list['Post']] = relationship(  # noqa: F821 # type: ignore
        'Post',
        init=False,
        secondary='posts_tags',
        back_populates='tags',
        lazy='selectin',
        join_depth=2,
    )
