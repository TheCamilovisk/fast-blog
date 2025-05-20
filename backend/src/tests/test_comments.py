from http import HTTPStatus

import pytest

from src.schemas.comment import CreateCommentRequestSchema
from src.services.comment_service import CommentService


@pytest.mark.asyncio
async def test_add_comment_success(async_client, user, token, post):
    payload = {'post_id': post.id, 'content': 'Great post'}
    resp = await async_client.post(
        '/comments/',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert resp.status_code == HTTPStatus.CREATED

    body = resp.json()
    assert body['id'] == 1
    assert body['post_id'] == post.id
    assert body['content'] == 'Great post'


@pytest.mark.asyncio
async def test_list_comments(async_client, session, user, post):
    for i in range(15):
        payload = {
            'post_id': post.id,
            'content': f'Comment {i}',
            'parent_id': None,
        }
        await CommentService.add_comment(
            session=session,
            comment_data=CreateCommentRequestSchema(**payload),
            current_user=user,
        )

    resp = await async_client.get(f'/comments/post/{post.id}?offset=5&limit=5')
    assert resp.status_code == HTTPStatus.OK
    comments = resp.json()['comments']
    assert len(comments) == 5  # noqa: PLR2004
    assert comments[0]['content'] == 'Comment 5'


@pytest.mark.asyncio
async def test_add_reply_and_list(async_client, user, token, post, session):
    payload = {'post_id': post.id, 'content': 'First!'}
    parent = await CommentService.add_comment(
        session=session,
        comment_data=CreateCommentRequestSchema(**payload),
        current_user=user,
    )
    parent_id = parent.id

    reply = await async_client.post(
        '/comments/',
        json={
            'post_id': post.id,
            'content': 'Replying',
            'parent_id': parent_id,
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    reply_id = reply.json()['id']

    resp_list = await async_client.get(f'/comments/post/{post.id}')

    assert resp_list.status_code == HTTPStatus.OK
    comments = resp_list.json()['comments']
    top = comments[0]
    assert top['id'] == parent_id
    assert top['replies'][0]['id'] == reply_id
    assert top['replies'][0]['parent_id'] == parent_id


@pytest.mark.asyncio
async def test_list_comments_default_pagination(
    async_client, session, user, post
):
    for i in range(15):
        payload = {
            'post_id': post.id,
            'content': f'Comment {i}',
            'parent_id': None,
        }
        await CommentService.add_comment(
            session=session,
            comment_data=CreateCommentRequestSchema(**payload),
            current_user=user,
        )

    resp = await async_client.get(f'/comments/post/{post.id}')
    assert resp.status_code == HTTPStatus.OK
    comments = resp.json()['comments']
    assert len(comments) == 10  # noqa: PLR2004
