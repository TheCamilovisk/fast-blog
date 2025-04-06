from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from api.app import app
from api.models import User, table_registry


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())
        yield _engine


@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 4, 5, 12, 0, 0)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

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


@pytest.fixture
def user(session, mock_db_time):
    with mock_db_time(model=User):
        user = User(
            username='defaultuser',
            password='password',
            email='defaultuser@example.com',
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        yield user
