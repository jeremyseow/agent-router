from pydantic import BaseModel
from typing import List, Optional
import logfire
from db.session import get_db_connection
import asyncpg

class AgentConfig(BaseModel):
    agent_name: str
    role_prompt: str
    system_prompt: str
    enabled_tools: List[str]

async def get_agent_config(agent_name: str, pool: asyncpg.Pool) -> Optional[AgentConfig]:
    """Retrieves agent prompt limits and tools from DB."""
    logfire.info(f"Fetching agent config for {agent_name}")
    async with get_db_connection(pool) as conn:
        row = await conn.fetchrow(
            "SELECT agent_name, role_prompt, system_prompt, enabled_tools FROM agent_configs WHERE agent_name = $1",
            agent_name
        )
        if row:
            # asyncpg returns lists directly for PostgreSQL array types
            return AgentConfig(
                agent_name=row['agent_name'],
                role_prompt=row['role_prompt'],
                system_prompt=row['system_prompt'],
                enabled_tools=row['enabled_tools']
            )
        logfire.warn(f"No config found for agent: {agent_name}")
        return None

async def get_all_agent_configs(pool: asyncpg.Pool) -> List[AgentConfig]:
    """Retrieves all agent configurations from DB."""
    logfire.info("Fetching all agent configurations")
    async with get_db_connection(pool) as conn:
        rows = await conn.fetch(
            "SELECT agent_name, role_prompt, system_prompt, enabled_tools FROM agent_configs"
        )
        return [
            AgentConfig(
                agent_name=row['agent_name'],
                role_prompt=row['role_prompt'],
                system_prompt=row['system_prompt'],
                enabled_tools=row['enabled_tools']
            ) for row in rows
        ]
