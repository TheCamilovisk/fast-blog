from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.core.database import get_session
from src.main import app
from src.models.user import User, table_registry
from src.schemas.posts import CreatePostRequestSchema
from src.services.post_service import PostService
from src.utils.security import create_access_token


@pytest.fixture(scope='session')
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


@pytest_asyncio.fixture
async def async_client(session) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that provides a TestClient for the FastAPI app.
    """

    def get_session_override():
        return session

    transport = ASGITransport(app)
    async with AsyncClient(
        transport=transport, base_url='http://test'
    ) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session) -> User:
    password = 'S3cur3!'
    user = User.create(
        username='dave',
        email='dave@example.com',
        password=password,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def another_user(session) -> User:
    password = 'S3cr3|!'
    user = User.create(
        username='faust',
        email='faust@example.com',
        password=password,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def token(user) -> str:
    payload = {'sub': user.username}
    access_token = create_access_token(payload)
    return access_token


@pytest_asyncio.fixture
async def another_token(another_user) -> str:
    payload = {'sub': another_user.username}
    access_token = create_access_token(payload)
    return access_token


@pytest_asyncio.fixture
async def post(session, user):
    payload = {
        'title': 'Test Post 1',
        'subtitle': 'Test 1',
        'content': 'The content 1',
    }
    post = await PostService.create_post(
        session=session,
        post_data=CreatePostRequestSchema(**payload),
        author=user,
    )
    return post


@pytest_asyncio.fixture
async def another_post(session, user):
    payload = {
        'title': 'Test Post 2',
        'subtitle': 'Test 2',
        'content': 'The content 2',
    }
    post = await PostService.create_post(
        session=session,
        post_data=CreatePostRequestSchema(**payload),
        author=user,
    )
    return post
