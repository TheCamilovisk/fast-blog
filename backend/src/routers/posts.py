from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from src.core.dependencies import CurrentUser, DBSession, PageFilter
from src.schemas.posts import (
    CreatePostRequestSchema,
    PostListResponseSchema,
    PostResponseSchema,
)
from src.services.post_service import PostService

router = APIRouter(prefix='/posts', tags=['posts'])


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_post(
    post_data: CreatePostRequestSchema,
    session: DBSession,
    current_user: CurrentUser,
) -> PostResponseSchema:
    """
    Create a post owned by the authenticated user.
    """
    post = await PostService.create_post(
        session=session, post_data=post_data, author=current_user
    )
    return post


@router.get('/', status_code=HTTPStatus.OK)
async def list_posts(
    session: DBSession, filter: PageFilter
) -> PostListResponseSchema:
    posts = await PostService.list_published(
        session=session, offset=filter.offset, limit=filter.limit
    )
    return {'pagination': filter, 'posts': posts}


@router.get('/{post_id}', status_code=HTTPStatus.OK)
async def get_post(post_id: int, session: DBSession):
    post = await PostService.get_post(session=session, post_id=post_id)
    if not post or not post.is_published:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Post not found'
        )
    return post
