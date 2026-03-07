import httpx
import logfire
from typing import Optional, Dict
from pydantic_ai import RunContext
from db.agent_config import get_agent_config
from models.dependencies import AgentDependencies

async def make_get_request(ctx: RunContext[AgentDependencies], url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """Makes a GET request to an external HTTP API and returns the text response."""
    if isinstance(ctx.deps, AgentDependencies):
        config = await get_agent_config(ctx.deps.agent_name, ctx.deps.db_pool)
        if not config or "api_get" not in config.enabled_tools:
            return "Error: Permission denied. You do not have 'api_get' capability."
            
    logfire.info(f"Agent making GET request to: {url}")
    async with httpx.AsyncClient() as client:
        try:
            # Don't pass None headers to avoid httpx bugs, use empty dict
            request_headers = headers or {}
            response = await client.get(url, headers=request_headers, timeout=10.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logfire.error(f"API GET request failed: {url} with error {e}")
            return f"API GET Request failed: {e}"

async def make_post_request(ctx: RunContext[AgentDependencies], url: str, json_data: dict, headers: Optional[Dict[str, str]] = None) -> str:
    """Makes a POST request to an external HTTP API and returns the text response."""
    if isinstance(ctx.deps, AgentDependencies):
        config = await get_agent_config(ctx.deps.agent_name, ctx.deps.db_pool)
        if not config or "api_post" not in config.enabled_tools:
            return "Error: Permission denied. You do not have 'api_post' capability."
            
    logfire.info(f"Agent making POST request to: {url}")
    async with httpx.AsyncClient() as client:
        try:
            request_headers = headers or {}
            response = await client.post(url, json=json_data, headers=request_headers, timeout=10.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logfire.error(f"API POST request failed: {url} with error {e}")
            return f"API POST Request failed: {e}"
