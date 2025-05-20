from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from src.core.dependencies import CurrentUser, DBSession, PageFilter
from src.schemas.comment import (
    CommentListResponseSchema,
    CommentResponseSchema,
    CreateCommentRequestSchema,
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
