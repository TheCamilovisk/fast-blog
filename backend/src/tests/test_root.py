from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_read_root(async_client):
    response = await async_client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Welcome to Fast Blog!'}
