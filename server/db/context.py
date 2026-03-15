import logfire
import asyncpg
from typing import Optional
from db.session import get_db_connection

async def load_chat_session(session_id: str, pool: asyncpg.Pool) -> Optional[str]:
    """
    Loads the summarized conversation history for a given session_id.
    """
    logfire.info(f"Loading chat session memory for {session_id}")
    async with get_db_connection(pool) as conn:
        row = await conn.fetchrow(
            "SELECT summary FROM chat_sessions WHERE session_id = $1", 
            session_id
        )
        if row and row['summary']:
            return row['summary']
        
        logfire.info(f"No previous session memory found for {session_id}")
        return None

async def save_chat_session(session_id: str, summary: str, pool: asyncpg.Pool):
    """
    Persists the dense conversation summary to the PostgreSQL database for the given session_id.
    """
    logfire.info(f"Saving chat session memory for {session_id}")
    
    async with get_db_connection(pool) as conn:
        await conn.execute("""
            INSERT INTO chat_sessions (session_id, summary, updated_at)
            VALUES ($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT (session_id) DO UPDATE 
            SET summary = EXCLUDED.summary,
                updated_at = CURRENT_TIMESTAMP;
        """, session_id, summary)
