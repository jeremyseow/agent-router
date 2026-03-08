import logfire
import asyncpg
from typing import List, Optional
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from db.session import get_db_connection

async def load_chat_session(session_id: str, pool: asyncpg.Pool, limit: int = 3) -> List[ModelMessage]:
    """
    Loads the conversation history for a given session_id.
    Implements a Sliding Window by loading only the most recent N messages.
    """
    logfire.info(f"Loading chat session memory for {session_id}")
    async with get_db_connection(pool) as conn:
        row = await conn.fetchrow(
            "SELECT messages FROM chat_sessions WHERE session_id = $1", 
            session_id
        )
        if row and row['messages']:
            try:
                # Validate JSON directly into Pydantic AI ModelMessage arrays
                messages = ModelMessagesTypeAdapter.validate_json(row['messages'])
                
                # Sliding Window: Return only the last `limit` messages to prevent context exhaustion
                return messages[-limit:] if limit else messages
            except Exception as e:
                logfire.error(f"Failed to deserialize messages for {session_id}: {e}")
                return []
        
        logfire.info(f"No previous session memory found for {session_id}")
        return []

async def save_chat_session(session_id: str, messages: List[ModelMessage], pool: asyncpg.Pool):
    """
    Persists the conversation history to the PostgreSQL database for the given session_id.
    """
    logfire.info(f"Saving chat session memory for {session_id}")
    
    # Dump Pydantic AI messages to JSON bytes
    messages_json = ModelMessagesTypeAdapter.dump_json(messages).decode('utf-8')
    
    async with get_db_connection(pool) as conn:
        await conn.execute("""
            INSERT INTO chat_sessions (session_id, messages, updated_at)
            VALUES ($1, $2::jsonb, CURRENT_TIMESTAMP)
            ON CONFLICT (session_id) DO UPDATE 
            SET messages = EXCLUDED.messages,
                updated_at = CURRENT_TIMESTAMP;
        """, session_id, messages_json)
