import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
from core.config import settings
import logfire

_pool: Optional[asyncpg.Pool] = None

async def init_db_pool():
    global _pool
    if _pool is None:
        logfire.info(f"Initializing asyncpg database pool (SSL: {settings.postgres_ssl_enabled})")
        _pool = await asyncpg.create_pool(
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            host=settings.postgres_host,
            port=settings.postgres_port,
            ssl=settings.is_ssl_enabled,
            min_size=1,
            max_size=10
        )

async def close_db_pool():
    global _pool
    if _pool:
        logfire.info("Closing asyncpg database pool")
        await _pool.close()
        _pool = None

@asynccontextmanager
async def get_db_connection():
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Call init_db_pool() first.")
    async with _pool.acquire() as connection:
        yield connection
