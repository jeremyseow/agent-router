import os
import logfire
from pydantic_ai import Agent, RunContext
from core.config import settings

from db.agent_config import get_agent_config, get_all_agent_configs
from tools.registry import AVAILABLE_TOOLS

if settings.gemini_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.gemini_api_key

# Expose an empty registry that will be populated dynamically at startup
worker_registry = {}

# Define dynamic system prompt loader
async def _get_dynamic_prompt(ctx: RunContext[str]) -> str:
    agent_name = ctx.deps
    config = await get_agent_config(agent_name)
    if config:
        return config.system_prompt
    return f"You are a helpful {agent_name} agent."

async def init_workers():
    """Initializes worker agents dynamically based on the DB configurations."""
    global worker_registry
    worker_registry.clear()
    
    configs = await get_all_agent_configs()
    for config in configs:
        logfire.info(f"Dynamically loading worker: {config.agent_name} with tools: {config.enabled_tools}")
        agent = Agent('gemini-2.5-flash', deps_type=str)
        
        # Register system prompt loader
        agent.system_prompt(_get_dynamic_prompt)
        
        # Attach enabled tools by referencing our application registry
        for tool_name in config.enabled_tools:
            if tool_name in AVAILABLE_TOOLS:
                agent.tool(AVAILABLE_TOOLS[tool_name])
            else:
                logfire.warn(f"Unknown tool specified for {config.agent_name}: {tool_name}")
                
        worker_registry[config.agent_name] = agent
    
    logfire.info(f"Finished loading {len(worker_registry)} agents into the worker registry.")
