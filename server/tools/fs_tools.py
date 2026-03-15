import os
import logfire
from pydantic_ai import RunContext
from db.agent_config import get_agent_config
from models.dependencies import AgentDependencies

AGENT_OUTPUT_DIR = "agent_output"

async def read_file(ctx: RunContext[AgentDependencies], filepath: str) -> str:
    """Reads a file from the file system. Ensure the filepath is relative to the project root or absolute."""
    if isinstance(ctx.deps, AgentDependencies):
        config = await get_agent_config(ctx.deps.agent_name, ctx.deps.db_pool)
        if not config or "read_fs" not in config.enabled_tools:
            return "Error: Permission denied. You do not have 'read_fs' capability."
            
    try:
        logfire.info(f"Agent reading file: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logfire.error(f"Error reading file {filepath}: {e}")
        return f"Error reading file {filepath}: {e}"

async def write_file(ctx: RunContext[AgentDependencies], filepath: str, content: str) -> str:
    """Writes content to a file. The file will ALWAYS be saved inside the directory specified by AGENT_OUTPUT_DIR, regardless of the path provided."""
    if isinstance(ctx.deps, AgentDependencies):
        config = await get_agent_config(ctx.deps.agent_name, ctx.deps.db_pool)
        if not config or "write_fs" not in config.enabled_tools:
            return "Error: Permission denied. You do not have 'write_fs' capability."
            
    try:
        sandbox_dir = os.path.abspath(AGENT_OUTPUT_DIR)
        clean_path = filepath.lstrip('/\\')
        
        # Resolve the absolute path of the intended file
        final_path = os.path.abspath(os.path.join(sandbox_dir, clean_path))        
        if not final_path.startswith(sandbox_dir):
            return f"Error: Directory traversal blocked. You can only write into the {AGENT_OUTPUT_DIR} directory."
            
        logfire.info(f"Agent writing file to restricted output directory: {final_path}")
        directory = os.path.dirname(os.path.abspath(final_path))
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {final_path}"
    except Exception as e:
        logfire.error(f"Error writing file {filepath}: {e}")
        return f"Error writing file {filepath}: {e}"
