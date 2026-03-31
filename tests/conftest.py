from datetime import datetime
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import asyncpg
import os

from server.main import app
from server.db.database import get_connection
from server.schemas.user import UserInDB, UserRole

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:password@localhost:5433/bearcat_test"
)

#=====================#
# Real DB Fixtures    #
#=====================#

@pytest_asyncio.fixture  # ← function scope, fresh every test
async def test_conn():
    """
    Creates a brand new pool and connection per test.
    Rolls back after each test to keep DB clean.
    No session scope = no event loop conflicts.
    """
    pool = await asyncpg.create_pool(TEST_DATABASE_URL)

    async with pool.acquire() as conn:
        # Apply schema fresh for this connection
        with open("sql/schema.sql", "r") as f:
            schema = f.read()
        await conn.execute(schema)

        transaction = conn.transaction()
        await transaction.start()

        yield conn  # ← test runs here

        await transaction.rollback()  # ← always clean up

    await pool.close()

#==============================#
# Reusable Mock Data Factories #
#==============================#

@pytest.fixture
def make_mock_user():
    def _factory(**overrides):
        defaults = dict(
            id=uuid4(),
            email="testuser@mail.uc.edu",
            username="testuser",
            role=UserRole.student,
            is_email_verified=True,
            admin_approved=False,
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return UserInDB(**{**defaults, **overrides})

    return _factory

#============================#
# Mock DB Connection Fixture #
#============================#

@pytest.fixture
def mock_conn():
    conn = MagicMock()
    conn.fetchrow = AsyncMock()
    conn.execute = AsyncMock()
    conn.fetch = AsyncMock()
    return conn

#=====================#
# Test Client Fixture #
#=====================#

@pytest_asyncio.fixture
async def client(mock_conn):
    app.dependency_overrides[get_connection] = lambda: mock_conn

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()