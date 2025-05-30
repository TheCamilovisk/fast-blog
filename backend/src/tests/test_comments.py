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
async def test_unauthenticated_cannot_comment(async_client, post):
    resp = await async_client.post(
        '/comments/', json={'post_id': post.id, 'content': 'No auth'}
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json()['detail'] == 'Not authenticated'


@pytest.mark.asyncio
async def test_comment_nonexistent_post_returns_400(async_client, user, token):
    resp = await async_client.post(
        '/comments/',
        json={'post_id': 999, 'content': 'Should fail'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST


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


@pytest.mark.asyncio
async def test_delete_comment_success(async_client, token, comment):
    resp = await async_client.delete(
        f'/comments/{comment.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_comment_forbidden(async_client, another_token, comment):
    resp = await async_client.delete(f'/comments/{comment.id}')
    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    resp = await async_client.delete(
        f'/comments/{comment.id}',
        headers={'Authorization': f'Bearer {another_token}'},
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_comment_success(async_client, token, comment):
    payload = {'content': 'Edited'}
    resp = await async_client.put(
        f'/comments/{comment.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()['content'] == payload['content']


@pytest.mark.asyncio
async def test_update_comment_forbidden(async_client, another_token, comment):
    payload = {'content': 'Edited'}
    resp = await async_client.put(
        f'/comments/{comment.id}',
        json=payload,
        headers={'Authorization': f'Bearer {another_token}'},
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_comment_not_found(async_client, token):
    payload = {'content': 'Edited'}
    resp = await async_client.put(
        '/comments/999',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND
