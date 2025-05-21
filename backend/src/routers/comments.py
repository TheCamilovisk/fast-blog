from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from src.core.dependencies import CurrentUser, DBSession, PageFilter
from src.schemas.comment import (
    CommentListResponseSchema,
    CommentResponseSchema,
    CreateCommentRequestSchema,
    UpdateCommentRequestSchema,
)
from src.services.comment_service import CommentService

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_comment(
    comment_data: CreateCommentRequestSchema,
    session: DBSession,
    current_user: CurrentUser,
) -> CommentResponseSchema:
    try:
        comment = await CommentService.add_comment(
            session=session,
            comment_data=comment_data,
            current_user=current_user,
        )
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
    return comment


@router.get('/post/{post_id}', status_code=HTTPStatus.OK)
async def list_comments(
    post_id: int, session: DBSession, filter: PageFilter
) -> CommentListResponseSchema:
    comments = await CommentService.list_comments(
        session=session,
        post_id=post_id,
        offset=filter.offset,
        limit=filter.limit,
    )
    return {'pagination': filter, 'comments': comments}


@router.delete('/{comment_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_comment(
    comment_id: int, session: DBSession, current_user: CurrentUser
) -> None:
    try:
        await CommentService.delete_comment(
            session=session, comment_id=comment_id, current_user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(e))


@router.put('/{comment_id}', status_code=HTTPStatus.OK)
async def update_comment(
    comment_id: int,
    comment_data: UpdateCommentRequestSchema,
    session: DBSession,
    current_user: CurrentUser,
) -> CommentResponseSchema:
    try:
        comment = await CommentService.update_comment(
            session=session,
            comment_id=comment_id,
            comment_data=comment_data,
            current_user=current_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(e))
    return comment
