from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.models.user import User


@pytest.mark.asyncio
async def test_user_create_ok(session, mock_db_time):
    with mock_db_time(model=User) as time:
        user = User(
            username='testuser',
            password='securepassword',
            email='test@example.com',
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    db_user = await session.scalar(
        select(User).filter(User.username == 'testuser')
    )

    assert asdict(db_user) == {
        'id': user.id,
        'username': 'testuser',
        'password': 'securepassword',
        'email': 'test@example.com',
        'created_at': time,
        'updated_at': time,
        'superuser': False,
        'profile': None,
    }


@pytest.mark.asyncio
async def test_user_unique_username_error(session, user):
    duplicate_user = User(
        username=user.username,
        password='password2',
        email='duplicate@example.com',
    )
    session.add(duplicate_user)

    with pytest.raises(IntegrityError) as e:
        await session.commit()

    assert 'username' in str(e.value.orig)


@pytest.mark.asyncio
async def test_user_unique_email_error(session, user):
    duplicate_user = User(
        username='anotheruniqueuser',
        password='password2',
        email=user.email,
    )
    session.add(duplicate_user)

    with pytest.raises(IntegrityError) as e:
        await session.commit()

    assert 'email' in str(e.value.orig)


@pytest.mark.asyncio
async def test_user_update_username_ok(session, user):
    user.username = 'newusername'
    await session.commit()
    await session.refresh(user)

    updated_user = await session.scalar(select(User).filter_by(id=user.id))
    assert updated_user.username == 'newusername'


@pytest.mark.asyncio
async def test_user_update_username_exists_error(session, user, another_user):
    another_user.username = user.username

    with pytest.raises(IntegrityError) as e:
        await session.commit()

    assert 'username' in str(e.value.orig)


@pytest.mark.asyncio
async def test_user_update_email_ok(session, user):
    user.email = 'new@example.com'
    await session.commit()
    await session.refresh(user)

    updated_user = await session.scalar(select(User).filter_by(id=user.id))
    assert updated_user.email == 'new@example.com'


@pytest.mark.asyncio
async def test_user_update_email_exists_error(session, user, another_user):
    another_user.email = user.email

    with pytest.raises(IntegrityError) as e:
        await session.commit()

    assert 'email' in str(e.value.orig)


@pytest.mark.asyncio
async def test_user_update_password_ok(session, user):
    user.password = 'newpassword'

    updated_user = await session.scalar(
        select(User).filter(User.id == user.id)
    )
    assert updated_user.password == 'newpassword'


@pytest.mark.asyncio
async def test_user_delete_ok(session, user):
    await session.delete(user)
    await session.commit()

    deleted_user = await session.scalar(
        select(User).filter(User.id == user.id)
    )
    assert deleted_user is None


@pytest.mark.asyncio
async def test_user_get_by_username_or_email_ok(session, user):
    found_user = await session.scalar(
        select(User).filter(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.username == user.username
    assert found_user.email == user.email


@pytest.mark.asyncio
async def test_user_get_by_username_or_email_nonexistent(session):
    nonexistent_user = await session.scalar(
        select(User).filter(
            (User.username == 'nonexistentuser')
            | (User.email == 'nonexistent@example.com')
        )
    )

    assert nonexistent_user is None


@pytest.mark.asyncio
async def test_make_superuser_ok(session, user):
    user.superuser = True
    await session.commit()
    await session.refresh(user)

    updated_user = await session.scalar(
        select(User).filter(User.id == user.id)
    )
    assert updated_user.superuser is True
