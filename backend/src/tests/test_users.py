from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_create_user_success(async_client):
    payload = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'S3cur3P@ssw0rd',
    }
    resp = await async_client.post('/users/', json=payload)
    assert resp.status_code == HTTPStatus.CREATED
    body = resp.json()
    assert body['id'] == 1
    assert body['username'] == 'alice'
    assert body['email'] == 'alice@example.com'
    assert body['is_active']
    assert body['posts'] == []
    assert not body['is_superuser']


@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client):
    await async_client.post(
        '/users/',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'An0therP@ss',
        },
    )
    resp = await async_client.post(
        '/users/',
        json={
            'username': 'bobby',
            'email': 'bob@example.com',
            'password': 'Y3tAn0ther',
        },
    )
    assert resp.status_code == HTTPStatus.CONFLICT
    assert resp.json()['detail'] == 'Email already registered'
