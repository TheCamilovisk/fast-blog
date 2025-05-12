from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that provides a TestClient for the FastAPI app.
    """
    transport = ASGITransport(app)
    async with AsyncClient(
        transport=transport, base_url='http://test'
    ) as client:
        yield client
