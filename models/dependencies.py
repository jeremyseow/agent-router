from dataclasses import dataclass
import asyncpg
import typing
from pydantic_ai import Agent

@dataclass
class AgentDependencies:
    agent_name: str
    db_pool: asyncpg.Pool

@dataclass
class WorkerRegistration:
    agent: Agent
    description: str

@dataclass
class RouterDependencies:
    worker_registry: typing.Dict[str, WorkerRegistration]
    db_pool: asyncpg.Pool
