import pytest_asyncio
from uuid import uuid4

from server.services import users_service, listings_service
from server.schemas.auth import UserRegister
from server.schemas.listing import ListingCreate, ListingType

@pytest_asyncio.fixture
async def registered_user(test_conn):
    """A real user to act as listing owner."""
    return await users_service.register_user(test_conn, UserRegister(
        email="testuser@mail.uc.edu",
        username="testuser",
        password="SecurePassword123!"
    ))

@pytest_asyncio.fixture
async def sample_book(test_conn):
    """Insert a real book row for FK tests."""
    record = await test_conn.fetchrow(
        """
        INSERT INTO books (title, author, isbn13)
        VALUES ($1, $2, $3)
        RETURNING id, title, author, isbn13, created_at
        """,
        "Clean Code", "Robert C. Martin", "9780132350884"
    )
    return record

@pytest_asyncio.fixture
async def sample_department(test_conn):
    """Insert a real department for course FK tests."""
    record = await test_conn.fetchrow(
        """
        INSERT INTO departments (code, name)
        VALUES ($1, $2)
        RETURNING id, code, name
        """,
        "CS", "Computer Science"
    )
    return record

@pytest_asyncio.fixture
async def sample_course(test_conn, sample_department):
    """Insert a real course for FK tests."""
    record = await test_conn.fetchrow(
        """
        INSERT INTO courses (department_id, course_number, title)
        VALUES ($1, $2, $3)
        RETURNING id, department_id, course_number, title, created_at
        """,
        sample_department["id"], "101", "Intro to Computer Science"
    )
    return record

@pytest_asyncio.fixture
async def sample_listing(test_conn, registered_user):
    """A basic misc listing for tests that need an existing listing."""
    return await listings_service.create_listing(
        test_conn,
        ListingCreate(
            type=ListingType.misc,
            title="Old Desk Chair",
            description="Slightly worn but comfy",
            price_cents=2500,
            item_condition="Good"
        ),
        registered_user.id
    )