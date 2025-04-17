from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from api.app import app
from api.database import get_session, table_registry
from api.models.post import Post
from api.models.profile import Profile
from api.models.tag import Tag
from api.models.user import User
from api.security import create_access_token, get_password_hash


@pytest_asyncio.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 4, 5, 12, 0, 0)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time
        if hasattr(target, 'published_at'):
            target.published_at = time

    event.listen(
        model,
        'before_insert',
        fake_time_handler,
    )

    yield time

    event.remove(
        model,
        'before_insert',
        fake_time_handler,
    )


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session, mock_db_time):
    password = 'password'
    with mock_db_time(model=User):
        user = User(
            username='defaultuser',
            password=get_password_hash(password),
            email='defaultuser@example.com',
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        user.clean_password = password

        yield user


@pytest_asyncio.fixture
async def profile(session, user, mock_db_time):
    with mock_db_time(model=Profile):
        profile = Profile(
            bio='This is a test bio',
            website='https://example.com',
            firstname='John',
            lastname='Doe',
            user_id=user.id,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        yield profile


@pytest_asyncio.fixture
async def another_user(session, mock_db_time):
    password = 'anotherpassword'
    with mock_db_time(model=User):
        user = User(
            username='anotheruser',
            password=get_password_hash(password),
            email='anotheruser@example.com',
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        user.clean_password = password

        yield user


@pytest_asyncio.fixture
async def another_profile(session, another_user, profile, mock_db_time):
    with mock_db_time(model=Profile):
        profile = Profile(
            bio='This is another test bio',
            website='https://anotherexample.com',
            firstname='Jane',
            lastname='Smith',
            user_id=another_user.id,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        yield profile


@pytest.fixture
def user_token(user):
    return create_access_token({'sub': user.email, 'exp': 30})


@pytest_asyncio.fixture
async def tag(session, mock_db_time):
    with mock_db_time(model=Profile):
        tag = Tag(name='TestTag')
        session.add(tag)
        await session.commit()
        await session.refresh(tag)

        yield tag


@pytest_asyncio.fixture
async def post(session, profile, mock_db_time):
    with mock_db_time(model=Profile):
        post = Post(
            title='Test Post',
            subtitle='Test Subtitle',
            slug='test-post',
            content='This is the content of the test post.',
            author_id=profile.user_id,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)

        yield post
