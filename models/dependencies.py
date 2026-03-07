from dataclasses import dataclass
import asyncpg

@dataclass
class AgentDependencies:
    agent_name: str
    db_pool: asyncpg.Pool

@dataclass
class RouterDependencies:
    available_agents: list[str]
    db_pool: asyncpg.Pool
