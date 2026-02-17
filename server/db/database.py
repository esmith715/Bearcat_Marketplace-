import asyncpg
from typing import AsyncGenerator
from fastapi import Depends

# The connection string format should be changed as needed:
# "postgressql://username:password@localhost:5432/database-name"
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/bearcat-marketplace"

_pool: asyncpg.Pool | None = None


async def create_pool():
    global _pool
    _pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        # max_size=10
    )


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()


async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    async with _pool.acquire() as connection:
        yield connection
