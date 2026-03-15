import os
import logfire
import asyncpg
from pydantic_ai import Agent, RunContext
from core.config import settings

from db.agent_config import get_agent_config, get_all_agent_configs
from tools.registry import AVAILABLE_TOOLS, BUILTIN_TOOLS
from models.dependencies import AgentDependencies, WorkerRegistration


async def init_workers(pool: asyncpg.Pool) -> dict[str, WorkerRegistration]:
    """Initializes worker agents dynamically based on the DB configurations, returning the registry locally."""
    registry = {}
    
    configs = await get_all_agent_configs(pool)
    for config in configs:
        logfire.info(f"Dynamically loading worker: {config.agent_name} with tools: {config.enabled_tools}")
        
        # Instantiate optional builtins based on DB config tokens and BUILTIN_TOOLS mapping
        builtin_tools = []
        for tool_name in config.enabled_tools:
            if tool_name in BUILTIN_TOOLS:
                builtin_tools.append(BUILTIN_TOOLS[tool_name])
            
        agent = Agent(
            'gemini-2.5-flash', 
            deps_type=AgentDependencies, 
            defer_model_check=True, 
            builtin_tools=builtin_tools,
            system_prompt=config.system_prompt
        )
        
        # Attach enabled tools by referencing our application registry
        for tool_name in config.enabled_tools:
            if tool_name in AVAILABLE_TOOLS:
                agent.tool(AVAILABLE_TOOLS[tool_name])
            elif tool_name not in BUILTIN_TOOLS:
                logfire.warn(f"Unknown tool specified for {config.agent_name}: {tool_name}")
                
        registry[config.agent_name] = WorkerRegistration(
            agent=agent,
            description=config.role_prompt
        )
    
    logfire.info(f"Finished loading {len(registry)} agents into the worker registry.")
    return registry
