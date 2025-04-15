from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar('T')


class BaseRepository(Generic[T]):
    model: Type[T]

    @classmethod
    def get_by_id(cls, session: Session, obj_id: int) -> T | None:
        return session.scalar(select(cls.model).filter(cls.model.id == obj_id))

    @classmethod
    def list_all(
        cls, session: Session, limit: int = 10, offset: int = 0
    ) -> list[T]:
        return session.scalars(
            select(cls.model).offset(offset).limit(limit)
        ).all()

    @classmethod
    def create(cls, session: Session, **kwargs) -> T:
        obj = cls.model(**kwargs)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @classmethod
    def update(cls, session: Session, obj: T, **kwargs) -> T:
        for key, value in kwargs.items():
            if value is not None:
                setattr(obj, key, value)
        session.commit()
        session.refresh(obj)
        return obj

    @classmethod
    def delete(cls, session: Session, obj: T) -> None:
        session.delete(obj)
        session.commit()
