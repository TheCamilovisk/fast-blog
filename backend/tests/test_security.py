from jwt import decode

from api.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
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
