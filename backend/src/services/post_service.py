from sqlalchemy.ext.asyncio import AsyncSession

from src.models.post import Post
from src.models.user import User
from src.repositories.post_repository import PostRepository
from src.schemas.posts import CreatePostRequestSchema


class PostService:
    @staticmethod
    async def create_post(
        session: AsyncSession,
        post_data: CreatePostRequestSchema,
        author: User,
    ) -> Post:
        post = await PostRepository.create(
            session=session,
            title=post_data.title,
            subtitle=post_data.subtitle,
            content=post_data.content,
            author_id=author.id,
        )
        return post

    @staticmethod
    async def get_post(session: AsyncSession, post_id: int) -> Post | None:
        return await PostRepository.get_by_id(session=session, post_id=post_id)

    @staticmethod
    async def list_published(
        session: AsyncSession, offset: int = 0, limit: int = 10
    ) -> list[Post]:
        return await PostRepository.list_published(
            session=session, offset=offset, limit=limit
        )

    @staticmethod
    async def publish_post(
        session: AsyncSession, post_id: int, current_user: User
    ) -> Post:
        post = await PostRepository.get_by_id(session=session, post_id=post_id)

        if not post:
            raise ValueError('Post not found')

        if post.author_id != current_user.id:
            raise PermissionError(
                'User does not have permission to publish this post'
            )

        if post.is_published:
            return post

        post.publish()
        published_post = await PostRepository.save(session=session, post=post)
        return published_post

    @staticmethod
    async def unpublish_post(
        session: AsyncSession, post_id: int, current_user: User
    ) -> Post:
        post = await PostRepository.get_by_id(session=session, post_id=post_id)

        if not post:
            raise ValueError('Post not found')

        if post.author_id != current_user.id:
            raise PermissionError(
                'User does not have permission to unpublish this post'
            )

        if not post.is_published:
            return post

        post.unpublish()
        unpublished_post = await PostRepository.save(
            session=session, post=post
        )
        return unpublished_post
