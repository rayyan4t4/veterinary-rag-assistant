import os
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_vet.db"

import pytest
from httpx import ASGITransport, AsyncClient
from apps.api.app.main import app
from apps.api.app.db import engine
from apps.api.app.models import Base


@pytest.fixture(autouse=True)
async def database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as value:
        yield value


def auth(user="user-a", role="user"):
    return {"Authorization": f"Bearer test:{user}:{role}"}
