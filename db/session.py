import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
from core.config import settings
import logfire

async def init_db_pool() -> asyncpg.Pool:
    logfire.info(f"Initializing asyncpg database pool (SSL: {settings.postgres_ssl_enabled})")
    return await asyncpg.create_pool(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        port=settings.postgres_port,
        ssl=settings.is_ssl_enabled,
        min_size=1,
        max_size=10
    )

@asynccontextmanager
async def get_db_connection(pool: asyncpg.Pool):
    if pool is None:
        raise RuntimeError("Database pool object was None.")
    async with pool.acquire() as connection:
        yield connection
