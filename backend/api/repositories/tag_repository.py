from api.models.tag import Tag
from api.repositories.base_repository import BaseRepository


class TagRepository(BaseRepository[Tag]):
    model = Tag

    @classmethod
    def list(
        cls,
        session,
        pattern: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Tag]:
        query = session.query(cls.model)
        if pattern:
            query = query.filter(cls.model.name.ilike(f'%{pattern}%'))
        return query.offset(offset).limit(limit).all()
