from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.database import table_registry


@table_registry.mapped_as_dataclass
class RefreshToken:
    __tablename__ = 'refresh_tokens'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, default=func.now()
    )

    user = relationship(
        'User', back_populates='refresh_tokens', lazy='selectin'
    )
