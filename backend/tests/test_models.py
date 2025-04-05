from dataclasses import asdict

import pytest
from sqlalchemy.exc import IntegrityError

from api.models import User


def test_user_create_ok(session, mock_db_time):
    with mock_db_time(model=User) as time:
        user = User(
            username='testuser',
            password='securepassword',
            email='test@example.com',
        )
        session.add(user)
        session.commit()

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


def test_user_unique_username_error(session):
    user1 = User(
        username='uniqueuser', password='password1', email='unique@example.com'
    )
    session.add(user1)
    session.commit()

    user2 = User(
        username='uniqueuser',
        password='password2',
        email='duplicate@example.com',
    )
    session.add(user2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_user_unique_email_error(session):
    user1 = User(
        username='uniqueuser', password='password1', email='unique@example.com'
    )
    session.add(user1)
    session.commit()

    user2 = User(
        username='anotheruniqueuser',
        password='password2',
        email='unique@example.com',
    )
    session.add(user2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_user_creation_without_username_error():
    with pytest.raises(TypeError):
        User(password='securepassword', email='test@example.com')


def test_user_creation_without_email_error():
    with pytest.raises(TypeError):
        User(username='testuser', password='securepassword')


def test_user_creation_without_password_error():
    with pytest.raises(TypeError):
        User(username='testuser', email='test@example.com')


def test_user_update_username_ok(session, user):
    user.username = 'newusername'
    session.commit()

    updated_user = session.query(User).filter_by(id=user.id).first()
    assert updated_user.username == 'newusername'


def test_user_update_username_axists_error(session, user):
    user2 = User(
        username='anotheruser',
        password='password2',
        email='another@example.com',
    )
    session.add(user2)
    session.commit()

    user2.username = user.username
    with pytest.raises(IntegrityError):
        session.commit()


def test_user_update_email_ok(session, user):
    user.email = 'new@example.com'
    session.commit()

    updated_user = session.query(User).filter_by(id=user.id).first()
    assert updated_user.email == 'new@example.com'


def test_user_update_email_exists_error(session, user):
    user2 = User(
        username='anotheruser',
        password='password2',
        email='new@example.com',
    )
    session.add(user2)
    session.commit()

    user2.email = user.email
    with pytest.raises(IntegrityError):
        session.commit()


def test_user_update_password(session, user):
    user.password = 'newpassword'
    session.commit()

    updated_user = session.query(User).filter_by(id=user.id).first()
    assert updated_user.password == 'newpassword'
