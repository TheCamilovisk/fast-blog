from typing import Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.tag import Tag
from api.repositories.base_repository import BaseRepository


class TagRepository(BaseRepository[Tag]):
    model = Tag

    @classmethod
    async def list_all(
        cls,
        session: AsyncSession,
        pattern: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[int, list[Tag]]:
        query = select(Tag)
        if pattern:
            query = query.filter(Tag.name.ilike(f'%{pattern}%'))

        total = await cls.count_query(session, query)

        query = await session.scalars(query.offset(offset).limit(limit))
        return total, query.all()

    @classmethod
    async def find_or_create_multiple(
        cls,
        session: AsyncSession,
        tags: list[str],
    ) -> list[Tag]:
        tags = list(set(tags))
        query = await session.scalars(select(Tag).filter(Tag.name.in_(tags)))
        existing_tags = query.all()
        existing_tag_names = {tag.name for tag in existing_tags}
        new_tags = [
            Tag(name=tag) for tag in tags if tag not in existing_tag_names
        ]
        session.add_all(new_tags)
        await session.commit()
        for tag in new_tags:
            await session.refresh(tag)
        return existing_tags + new_tags
