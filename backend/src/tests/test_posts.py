from http import HTTPStatus

import pytest

from src.schemas.posts import CreatePostRequestSchema
from src.services.post_service import PostService


@pytest.mark.asyncio
async def test_create_post_success(async_client, user, token):
    post_payload = {
        'title': 'My Test Post',
        'subtitle': 'Testing',
        'content': 'Hello, World!',
    }
    resp = await async_client.post(
        '/posts/',
        json=post_payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert resp.status_code == HTTPStatus.CREATED
    body = resp.json()
    assert body['id'] == 1
    assert body['title'] == post_payload['title']
    assert body['subtitle'] == post_payload['subtitle']
    assert body['content'] == post_payload['content']
    assert body['slug'].startswith('my-test-post')
    assert body['author_id'] == user.id
    assert body['is_published'] is False


@pytest.mark.asyncio
async def test_list_posts_empty(async_client):
    resp = await async_client.get('/posts/')
    assert resp.status_code == HTTPStatus.OK
    body = resp.json()
    assert body['posts'] == []


@pytest.mark.asyncio
async def test_list_posts_pagination(async_client, user, token, session):
    for i in range(15):
        payload = {
            'title': f'Post {i}',
            'subtitle': f'Sub {i}',
            'content': '...',
        }
        post = await PostService.create_post(
            session=session,
            post_data=CreatePostRequestSchema(**payload),
            author=user,
        )
        await PostService.publish_post(
            session=session, post_id=post.id, current_user=user
        )

    resp = await async_client.get('/posts/?offset=5&limit=5')
    assert resp.status_code == HTTPStatus.OK
    posts = resp.json()['posts']
    assert len(posts) == 5  # noqa: PLR2004
    timestamps = [p['created_at'] for p in posts]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_post_variants(async_client, user, session):
    pub_payload = {
        'title': 'Published',
        'subtitle': 'Yes',
        'content': 'The content',
    }
    pub = await PostService.create_post(
        session=session,
        post_data=CreatePostRequestSchema(**pub_payload),
        author=user,
    )
    await PostService.publish_post(
        session=session, post_id=pub.id, current_user=user
    )

    unpub_payload = {
        'title': 'Draft',
        'subtitle': 'No',
        'content': 'Draft content',
    }
    unpub = await PostService.create_post(
        session=session,
        post_data=CreatePostRequestSchema(**unpub_payload),
        author=user,
    )

    resp_pub = await async_client.get(f'/posts/{pub.id}')
    assert resp_pub.status_code == HTTPStatus.OK
    assert resp_pub.json()['title'] == pub_payload['title']

    resp_unpub = await async_client.get(f'/posts/{unpub.id}')
    assert resp_unpub.status_code == HTTPStatus.NOT_FOUND

    resp_none = await async_client.get('posts/999')
    assert resp_none.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_unauthorized_create(async_client):
    payload = {
        'title': 'No Auth',
        'subtitle': 'Fail',
        'content': 'Should not work',
    }

    resp = await async_client.post('/posts/', json=payload)
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json()['detail'] == 'Not authenticated'


@pytest.mark.asyncio
async def test_publish_and_unpublish_by_author(async_client, token, post):
    auth_header = {'Authorization': f'Bearer {token}'}
    resp_pub = await async_client.post(
        f'/posts/{post.id}/publish', headers=auth_header
    )
    print(resp_pub.json())
    assert resp_pub.status_code == HTTPStatus.OK
    body = resp_pub.json()
    assert body['is_published'] is True
    assert body['published_at'] is not None

    resp_unpub = await async_client.post(
        f'/posts/{post.id}/unpublish', headers=auth_header
    )
    assert resp_unpub.status_code == HTTPStatus.OK
    body = resp_unpub.json()
    assert body['is_published'] is False
    assert body['published_at'] is None


@pytest.mark.asyncio
async def test_publish_and_unpublish_forbidden_for_other_user(
    async_client, token, another_token, post, another_post
):
    await async_client.post(
        f'/posts/{post.id}/publish',
        headers={'Authorization': f'Bearer {token}'},
    )

    invalid_auth_payload = {'Authorization': f'Bearer {another_token}'}

    respo_fobidden_pub = await async_client.post(
        f'/posts/{another_post.id}/publish', headers=invalid_auth_payload
    )
    assert respo_fobidden_pub.status_code == HTTPStatus.UNAUTHORIZED

    respo_fobidden_unpub = await async_client.post(
        f'/posts/{post.id}/unpublish', headers=invalid_auth_payload
    )
    assert respo_fobidden_unpub.status_code == HTTPStatus.UNAUTHORIZED
