from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.post import Post


class PostRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        title: str,
        subtitle: str,
        content: str,
        author_id: int,
    ) -> Post:
        post = Post.create(
            title=title,
            subtitle=subtitle,
            content=content,
            author_id=author_id,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def get_by_id(session: AsyncSession, post_id: int) -> Post | None:
        post = await session.scalar(select(Post).filter_by(id=post_id))
        return post

    @staticmethod
    async def list_published(
        session: AsyncSession, offset: int = 0, limit: int = 10
    ) -> list[Post]:
        query = (
            select(Post)
            .filter_by(is_published=True)
            .order_by(Post.published_at.desc())
            .offset(offset)
            .limit(limit)
        )
        posts = await session.scalars(query)
        return posts.all()

    @staticmethod
    async def save(session: AsyncSession, post: Post) -> Post:
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def delete(session: AsyncSession, post: Post) -> None:
        await session.delete(post)
        await session.commit()
