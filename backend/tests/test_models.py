from dataclasses import asdict

import pytest
from sqlalchemy.exc import IntegrityError

from api.models.user import User


def test_user_create_ok(session, mock_db_time):
    with mock_db_time(model=User) as time:
        User.create(
            session,
            username='testuser',
            password='securepassword',
            email='test@example.com',
        )

    db_user = session.query(User).filter_by(username='testuser').first()

    assert db_user is not None
    assert asdict(db_user) == {
        'id': 1,
        'username': 'testuser',
        'password': 'securepassword',
        'email': 'test@example.com',
        'created_at': time,
        'updated_at': time,
    }


def test_user_unique_username_error(session, user):
    with pytest.raises(IntegrityError) as e:
        User.create(
            session,
            username=user.username,
            password='password2',
            email='duplicate@example.com',
        )

    assert 'username' in str(e.value.orig)


def test_user_unique_email_error(session, user):
    with pytest.raises(IntegrityError) as e:
        User.create(
            session,
            username='anotheruniqueuser',
            password='password2',
            email=user.email,
        )

    assert 'email' in str(e.value.orig)


def test_user_update_username_ok(session, user):
    User.update(
        session,
        user=user,
        username='newusername',
    )

    updated_user = session.query(User).filter_by(id=user.id).first()
    assert updated_user.username == 'newusername'


def test_user_update_username_axists_error(session, user, another_user):
    with pytest.raises(IntegrityError) as e:
        User.update(
            session,
            user=another_user,
            username=user.username,
        )

    assert 'username' in str(e.value.orig)


def test_user_update_email_ok(session, user):
    User.update(session, user=user, email='new@example.com')

    updated_user = session.query(User).filter_by(id=user.id).first()
    assert updated_user.email == 'new@example.com'


def test_user_update_email_exists_error(session, user, another_user):
    with pytest.raises(IntegrityError) as e:
        User.update(session, user=another_user, email=user.email)

    assert 'email' in str(e.value.orig)


def test_user_update_password_ok(session, user):
    User.update_password(
        session,
        user=user,
        password='newpassword',
    )

    updated_user = session.query(User).filter_by(id=user.id).first()
    assert updated_user.password == 'newpassword'


def test_user_update_password_nonexistent_user(session):
    nonexistent_user_id = 9999
    user = session.query(User).filter_by(id=nonexistent_user_id).first()

    assert user is None

    user = User.update_password(
        session,
        user=user,
        password='newpassword',
    )

    assert user is None


def test_user_delete_ok(session, user):
    User.delete(session, user=user)

    deleted_user = session.query(User).filter_by(id=user.id).first()
    assert deleted_user is None


def test_user_delete_nonexistent_user(session):
    nonexistent_user_id = 9999
    user = session.query(User).filter_by(id=nonexistent_user_id).first()

    assert user is None

    user = User.delete(session, user=user)

    assert user is None


def test_user_get_by_username_or_email_ok(session, user):
    found_user = User.get_by_username_or_email(
        session,
        username_or_email=user.username,
    )

    assert found_user is not None
    assert found_user.id == user.id


def test_user_get_by_username_or_email_nonexistent(session):
    nonexistent_user = User.get_by_username_or_email(
        session,
        username_or_email='nonexistentuser',
    )

    assert nonexistent_user is None


def test_make_superuser_ok(session, user):
    User.make_superuser(session, user=user)

    updated_user = session.query(User).filter_by(id=user.id).first()
    assert updated_user.superuser is True


def test_make_superuser_nonexistent_user(session):
    nonexistent_user_id = 9999
    user = session.query(User).filter_by(id=nonexistent_user_id).first()

    assert user is None

    user = User.make_superuser(session, user=user)

    assert user is None
