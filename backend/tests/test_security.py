import pytest
from jwt import decode
from sqlalchemy import select

from api.models.user import User
from api.security import (
    ALGORITHM,
    SECRET_KEY,
    CredentialsException,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

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


def test_get_current_user_ok(session, user, user_token):
    result = get_current_user(session=session, token=user_token)

    assert result == user


def test_get_current_user_invalid_token(session, user):
    with pytest.raises(CredentialsException) as exc_info:
        get_current_user(session=session, token='invalidtoken')

    assert 'could not validate credentials' in str(exc_info.value).lower()


def test_get_current_user_user_not_found(session, user, user_token):
    db_user = session.scalar(select(User).filter(User.id == user.id))

    session.delete(db_user)
    session.commit()

    with pytest.raises(CredentialsException) as exc_info:
        get_current_user(session=session, token=user_token)

    assert 'could not validate credentials' in str(exc_info.value).lower()
