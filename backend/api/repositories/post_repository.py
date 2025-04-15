import copy
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.post import Post
from api.models.tag import Tag
from api.repositories.base_repository import BaseRepository


def slugify(title: str) -> str:
    return title.replace(' ', '-').lower() + '-' + uuid4().hex[:8]


class PostRespository(BaseRepository[Post]):
    model = Post

    @classmethod
    def list_all(  # noqa: PLR0913, PLR0917
        cls,
        session: Session,
        title: str = None,
        tags: list[str] = [],
        author_username: str = None,
        published_only: bool = False,
        published_at: datetime = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Post]:
        query = select(cls.model)

        if published_only:
            query = query.filter(cls.model.is_published.is_(True))

        if published_at:
            query = query.filter(cls.model.published_at >= published_at)

        if title:
            query = query.filter(
                cls.model.title.ilike(f'%{title}%')
                | cls.model.subtitle.ilike(f'%{title}%')
            )

        if tags:
            query = query.join(Post.tags).filter(Tag.name.in_(tags))

        if author_username:
            query = query.filter(
                cls.model.author.username.ilike(f'%{author_username}%')
            )

        query = (
            query.order_by(cls.model.published_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return session.scalars(query).all()

    @classmethod
    def create(cls, session: Session, **kwargs) -> Post:
        post_params = copy.copy(kwargs)
        for key, value in post_params.items():
            if key == 'is_published' and value is True:
                post_params['published_at'] = datetime.now()

        post_params['slug'] = slugify(post_params['title'])

        post = Post(**post_params)

        session.add(post)
        session.commit()
        session.refresh(post)
        return post

    @classmethod
    def add_tags(cls, session: Session, post: Post, tags: list[Tag]) -> Post:
        for tag in tags:
            if tag not in post.tags:
                post.tags.append(tag)

        session.commit()
        session.refresh(post)
        return post
