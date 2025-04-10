from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from api.database import table_registry


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
