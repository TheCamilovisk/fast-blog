from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from src.core.dependencies import CurrentUser, DBSession, PageFilter
from src.schemas.posts import (
    CreatePostRequestSchema,
    PostListResponseSchema,
    PostResponseSchema,
    UpdatePostRequestSchema,
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


@router.put('/{post_id}', status_code=HTTPStatus.OK)
async def update_post(
    post_id: int,
    post_data: UpdatePostRequestSchema,
    session: DBSession,
    current_user: CurrentUser,
) -> PostResponseSchema:
    try:
        post = await PostService.update_post(
            session=session,
            post_id=post_id,
            post_data=post_data,
            current_user=current_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(e))
    return post


@router.delete('/{post_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_post(
    post_id: int, session: DBSession, current_user: CurrentUser
) -> None:
    try:
        await PostService.delete_post(
            session=session, post_id=post_id, current_user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(e))


@router.post('/{post_id}/publish', status_code=HTTPStatus.OK)
async def publish_post(
    post_id: int, session: DBSession, current_user: CurrentUser
) -> PostResponseSchema:
    try:
        post = await PostService.publish_post(
            session=session, post_id=post_id, current_user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(e))
    return post


@router.post('/{post_id}/unpublish', status_code=HTTPStatus.OK)
async def unpublish_post(
    post_id: int, session: DBSession, current_user: CurrentUser
) -> PostResponseSchema:
    try:
        post = await PostService.unpublish_post(
            session=session, post_id=post_id, current_user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(e))
    return post
