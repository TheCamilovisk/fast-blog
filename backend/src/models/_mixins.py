from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def nowfunc():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default=nowfunc
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        init=False,
        default=nowfunc,
        onupdate=nowfunc,
    )
