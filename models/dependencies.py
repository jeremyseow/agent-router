from dataclasses import dataclass
import asyncpg

@dataclass
class AgentDependencies:
    agent_name: str
    db_pool: asyncpg.Pool

import typing

@dataclass
class RouterDependencies:
    worker_registry: typing.Dict[str, typing.Any]
    db_pool: asyncpg.Pool
