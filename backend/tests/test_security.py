from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode
from sqlalchemy import select

from api.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from api.models.user import User


def test_jwt():
    data = {'test': 'test'}
    token, _ = create_access_token(data)

    decoded = decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )
    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_get_password_hash():
    password = 'securepassword123'
    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert len(hashed_password) > 0


def test_verify_password():
    password = 'securepassword123'
    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password)
    assert not verify_password('wrongpassword', hashed_password)


@pytest.mark.asyncio
async def test_get_current_user_ok(session, user, user_token):
    result = await get_current_user(session=session, token=user_token)

    assert result == user


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(session, user):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(session=session, token='invalidtoken')

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert 'could not validate credentials' in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(session, user, user_token):
    db_user = await session.scalar(select(User).filter(User.id == user.id))

    await session.delete(db_user)
    await session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(session=session, token=user_token)

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert 'could not validate credentials' in str(exc_info.value).lower()
