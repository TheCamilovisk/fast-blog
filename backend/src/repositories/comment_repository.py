from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment


class CommentRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        content: str,
        post_id: int,
        author_id: int,
        parent: Comment | None = None,
    ) -> Comment:
        comment = Comment.create(
            content=content,
            post_id=post_id,
            author_id=author_id,
            parent=parent,
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment

    @staticmethod
    async def list_for_post(
        session: AsyncSession, post_id: int, offset: int = 0, limit: int = 10
    ) -> list[Comment]:
        query = (
            select(Comment)
            .filter_by(post_id=post_id, parent_id=None)
            .order_by(Comment.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.scalars(query)
        return result.all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int):
        query = select(Comment).filter_by(id=id)
        result = await session.scalar(query)
        return result

    @staticmethod
    async def delete(session: AsyncSession, comment: Comment) -> None:
        await session.delete(comment)
        await session.commit()

    @staticmethod
    async def save(session: AsyncSession, comment: Comment) -> Comment:
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment
