import copy
from datetime import datetime
from typing import Tuple
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.post import Post
from api.models.profile import Profile
from api.models.tag import Tag
from api.models.user import User
from api.repositories.base_repository import BaseRepository


def slugify(title: str) -> str:
    return title.replace(' ', '-').lower() + '-' + uuid4().hex[:8]


class PostRespository(BaseRepository[Post]):
    model = Post

    @classmethod
    async def list_all(  # noqa: PLR0913, PLR0917
        cls,
        session: AsyncSession,
        title: str = None,
        tags: list[str] = [],
        author_username: str = None,
        published_only: bool = False,
        published_at: datetime = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[int, list[Post]]:
        query = select(Post)

        if published_only:
            query = query.filter(Post.is_published.is_(True))

        if published_at:
            query = query.filter(Post.published_at >= published_at)

        if title:
            query = query.filter(
                Post.title.ilike(f'%{title}%')
                | Post.subtitle.ilike(f'%{title}%')
            )

        if tags:
            query = query.join(Post.tags).filter(Tag.name.in_(tags))

        if author_username:
            query = query.filter(
                Post.author.has(
                    Profile.user.has(
                        User.username.ilike(f'%{author_username}%')
                    )
                )
            )

        total = await cls.count_query(session, query)

        query = await session.scalars(
            query.order_by(Post.published_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return total, query.all()

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> Post:
        post_params = copy.copy(kwargs)
        for key, value in post_params.items():
            if key == 'is_published' and value is True:
                post_params['published_at'] = datetime.now()

        post_params['slug'] = slugify(post_params['title'])

        post = Post(**post_params)

        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @classmethod
    async def add_tags(
        cls, session: AsyncSession, post: Post, tags: list[Tag]
    ) -> Post:
        for tag in tags:
            if tag not in post.tags:
                post.tags.append(tag)

        await session.commit()
        await session.refresh(post)
        return post
