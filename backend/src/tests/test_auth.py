from http import HTTPStatus

import jwt
import pytest

from src.core.settings import get_settings
from src.schemas.token import RefreshTokenRequestSchema, TokenSchema
from src.utils.security import JWTTokenType

settings = get_settings()


@pytest.mark.asyncio
async def test_login_and_refresh(async_client, user):
    login_resp = await async_client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
        headers={'Content_Type': 'application/x-www-form-urlencoded'},
    )
    assert login_resp.status_code == HTTPStatus.CREATED
    token = TokenSchema(**login_resp.json())
    payload = jwt.decode(
        token.access_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
    )
    assert payload.get('sub') == user.username
    assert payload.get('type') == JWTTokenType.ACCESS.value

    refresh_resp = await async_client.post(
        '/auth/refresh', json={'refresh_token': token.refresh_token}
    )
    assert refresh_resp.status_code == HTTPStatus.CREATED
    new_token = TokenSchema(**refresh_resp.json())
    ap = jwt.decode(
        new_token.access_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
    )
    rp = jwt.decode(
        new_token.refresh_token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM,
    )
    assert ap.get('type') == JWTTokenType.ACCESS.value
    assert ap.get('sub') == user.username
    assert rp.get('type') == JWTTokenType.REFRESH.value
    assert rp.get('sub') == user.username


@pytest.mark.asyncio
async def test_refresh_invalid(async_client):
    bad = RefreshTokenRequestSchema(refresh_token='not.a.token')
    resp = await async_client.post('/auth/refresh', json=bad.model_dump())
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json()['detail'] == 'Invalid refresh token'
