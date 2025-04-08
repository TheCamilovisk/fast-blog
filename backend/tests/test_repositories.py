import pytest

from api import security
from api.repositories import (
    RepositoryConflictError,
    RepositoryNotFoundError,
    UserRepository,
)
from api.schemas import UserSchema, UserUpdateSchema


@pytest.fixture
def user_repository(session):
    return UserRepository(session)


def test_get_user_by_id_ok(user, user_repository):
    result = user_repository.get_user_by_id(1)

    assert result is not None
    assert result == user


def test_get_user_by_username_ok(user, user_repository):
    result = user_repository.get_user_by_username(user.username)

    assert result is not None
    assert result == user


def test_get_user_by_username_not_found(user_repository):
    result = user_repository.get_user_by_username('nonexistentuser')

    assert result is None


def test_get_user_by_email_ok(user, user_repository):
    result = user_repository.get_user_by_email(user.email)

    assert result is not None
    assert result == user


def test_get_user_by_email_not_found(user_repository):
    result = user_repository.get_user_by_email('nonexistentuser@email.com')

    assert result is None


def test_get_users_ok(user, another_user, user_repository):
    result = user_repository.get_users()

    assert len(result) == 2  # noqa: PLR2004
    assert user in result
    assert another_user in result


def test_create_user_ok(user_repository):
    new_user_data = UserSchema(
        username='testuser', email='test@example.com', password='password123'
    )
    result = user_repository.create_user(new_user_data)

    assert result is not None
    assert result.username == new_user_data.username
    assert result.email == new_user_data.email


def test_create_user_conflict_username(user, user_repository):
    user_data = UserSchema(
        username=user.username,
        email='test@example.com',
        password='password123',
    )

    with pytest.raises(RepositoryConflictError) as context:
        user_repository.create_user(user_data)

    assert str(context.value) == 'Username already exists.'


def test_create_user_conflict_email(user, user_repository):
    user_data = UserSchema(
        username='testuser',
        password='password123',
        email=user.email,
    )

    with pytest.raises(RepositoryConflictError) as context:
        user_repository.create_user(user_data)

    assert str(context.value) == 'Email already exists.'


def test_update_user_ok(user, user_repository):
    user_data = UserUpdateSchema(
        username='updateduser', email='updated@example.com'
    )
    result = user_repository.update_user(1, user_data)
    result = user_repository.get_user_by_id(1)

    assert result is not None
    assert result.username == user_data.username
    assert result.email == user_data.email


def test_update_user_not_found(user_repository):
    user_data = UserUpdateSchema(
        username='updateduser', email='updated@example.com'
    )

    with pytest.raises(RepositoryNotFoundError) as context:
        user_repository.update_user(1, user_data)

    assert str(context.value) == 'User not found.'


def test_update_user_conflict_username(user, another_user, user_repository):
    user_data = UserUpdateSchema(username=user.username)

    with pytest.raises(RepositoryConflictError) as context:
        user_repository.update_user(2, user_data)

    assert str(context.value) == 'Username already exists.'


def test_update_user_conflict_email(user, another_user, user_repository):
    user_data = UserUpdateSchema(email=user.email)

    with pytest.raises(RepositoryConflictError) as context:
        user_repository.update_user(2, user_data)

    assert str(context.value) == 'Email already exists.'


def test_update_user_password_ok(user, user_repository):
    new_password = 'newsecurepassword'
    user_data = UserUpdateSchema(password=new_password)

    result = user_repository.update_user(user.id, user_data)

    db_user = user_repository.get_user_by_id(user.id)

    assert result is not None
    assert result.id == user.id
    assert result.username == user.username
    assert result.email == user.email
    assert result.password != new_password
    assert security.verify_password(new_password, db_user.password)


def test_delete_user_ok(user, user_repository):
    user_repository.delete_user(1)


def test_delete_user_not_found(user_repository):
    with pytest.raises(RepositoryNotFoundError) as context:
        user_repository.delete_user(1)

    assert str(context.value) == 'User not found.'
