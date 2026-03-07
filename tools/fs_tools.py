import os
import logfire
from pydantic_ai import RunContext
from db.agent_config import get_agent_config

# We use generic dict as context placeholder if needed later
# In Pydantic AI, tools are decorated.

async def read_file(ctx: RunContext, filepath: str) -> str:
    """Reads a file from the file system. Ensure the filepath is relative to the project root or absolute."""
    if isinstance(ctx.deps, str):
        config = await get_agent_config(ctx.deps)
        if not config or "read_fs" not in config.enabled_tools:
            return "Error: Permission denied. You do not have 'read_fs' capability."
            
    try:
        logfire.info(f"Agent reading file: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logfire.error(f"Error reading file {filepath}: {e}")
        return f"Error reading file {filepath}: {e}"

async def write_file(ctx: RunContext, filepath: str, content: str) -> str:
    """Writes content to a file. Ensure the filepath is relative to the project root or absolute."""
    if isinstance(ctx.deps, str):
        config = await get_agent_config(ctx.deps)
        if not config or "write_fs" not in config.enabled_tools:
            return "Error: Permission denied. You do not have 'write_fs' capability."
            
    try:
        logfire.info(f"Agent writing file: {filepath}")
        directory = os.path.dirname(os.path.abspath(filepath))
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        logfire.error(f"Error writing file {filepath}: {e}")
        return f"Error writing file {filepath}: {e}"
