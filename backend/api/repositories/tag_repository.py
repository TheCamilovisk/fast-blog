from sqlalchemy.orm import Session

from api.models.tag import Tag
from api.repositories.base_repository import BaseRepository


class TagRepository(BaseRepository[Tag]):
    model = Tag

    @classmethod
    def list_all(
        cls,
        session: Session,
        pattern: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Tag]:
        query = session.query(Tag)
        if pattern:
            query = query.filter(Tag.name.ilike(f'%{pattern}%'))
        return query.offset(offset).limit(limit).all()

    @classmethod
    def find_or_create_multiple(
        cls,
        session: Session,
        tags: list[str],
    ) -> list[Tag]:
        tags = list(set(tags))
        existing_tags = session.query(Tag).filter(Tag.name.in_(tags)).all()
        existing_tag_names = {tag.name for tag in existing_tags}
        new_tags = [
            Tag(name=tag) for tag in tags if tag not in existing_tag_names
        ]
        session.add_all(new_tags)
        session.commit()
        return existing_tags + new_tags
