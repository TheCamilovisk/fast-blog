from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment
from src.models.user import User
from src.repositories.comment_repository import CommentRepository
from src.schemas.comment import (
    CreateCommentRequestSchema,
    UpdateCommentRequestSchema,
)


class CommentService:
    @staticmethod
    async def add_comment(
        session: AsyncSession,
        comment_data: CreateCommentRequestSchema,
        current_user: User,
    ) -> Comment:
        if comment_data.parent_id:
            parent = await CommentRepository.get_by_id(
                session=session, id=comment_data.parent_id
            )
            if not parent:
                raise RuntimeError('Parent post not found')
        else:
            parent = None
        comment = await CommentRepository.create(
            session=session,
            content=comment_data.content,
            post_id=comment_data.post_id,
            author_id=current_user.id,
            parent=parent,
        )
        return comment

    @staticmethod
    async def list_comments(
        session: AsyncSession, post_id: int, offset: int = 0, limit: int = 10
    ) -> list[Comment]:
        comments = await CommentRepository.list_for_post(
            session=session, post_id=post_id, offset=offset, limit=limit
        )
        return comments

    @staticmethod
    async def delete_comment(
        session: AsyncSession, comment_id: int, current_user: User
    ) -> None:
        comment = await CommentRepository.get_by_id(
            session=session, id=comment_id
        )
        if not comment:
            raise ValueError('Comment not found')
        if comment.author_id != current_user.id:
            raise PermissionError('Not allowed')
        await CommentRepository.delete(session=session, comment=comment)

    @staticmethod
    async def update_comment(
        session: AsyncSession,
        comment_id: int,
        comment_data: UpdateCommentRequestSchema,
        current_user: User,
    ) -> Comment:
        comment = await CommentRepository.get_by_id(
            session=session, id=comment_id
        )
        if not comment:
            raise ValueError('Comment not found')
        if comment.author_id != current_user.id:
            raise PermissionError('Not allowed')
        comment.update(comment_data.content)
        comment = await CommentRepository.save(
            session=session, comment=comment
        )
        return comment
