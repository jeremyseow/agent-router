from pydantic_ai import Agent, RunContext
from core.config import settings
import os
import logfire
from models.dependencies import RouterDependencies, AgentDependencies

# We removed output_type structured constraints so the router can converse freely
router_agent = Agent(
    'gemini-2.5-flash',
    deps_type=RouterDependencies,
    defer_model_check=True,
    retries=2
)

@router_agent.system_prompt
async def get_system_prompt(ctx: RunContext[RouterDependencies]) -> str:
    # Build a rich string describing each available worker and their exact job description
    agent_descriptions = "\n".join(
        f"- **{name}**: {registration.description}" 
        for name, registration in ctx.deps.worker_registry.items()
    ) if ctx.deps.worker_registry else "No workers available."

    return (
        "You are the main Supervising Orchestrator coordinating complex tasks on behalf of the user.\n"
        "You have access to the following specialized Worker Agents. Read their descriptions "
        "carefully to decide which one(s) are best equipped to handle the task:\n"
        f"{agent_descriptions}\n\n"
        "If the user asks for a simple conversational question, answer it directly.\n"
        "If the user asks for something complex requiring research, coding, or managing files, "
        "you MUST invoke the `delegate_to_worker` tool to dispatch the subtasks to the appropriate worker agent(s).\n"
        "You can invoke multiple tools in parallel if tasks are independent (e.g., asking a PM and an Engineer simultaneously).\n"
        "Wait for the workers to return their results, synthesize their findings, and return a final cohesive response to the user."
    )

@router_agent.tool
async def delegate_to_worker(
    ctx: RunContext[RouterDependencies], 
    worker_name: str, 
    task_description: str
) -> str:
    """Delegates a specialized task to a worker agent. You can call this multiple times in parallel for different workers."""
    if worker_name not in ctx.deps.worker_registry:
        return f"Error: Worker '{worker_name}' not found. Available targets: {list(ctx.deps.worker_registry.keys())}"
    
    logfire.info(f"Router delegating to {worker_name}: {task_description[:50]}...")
    worker_registration = ctx.deps.worker_registry[worker_name]
    worker = worker_registration.agent
    
    # Create strict execution isolation for the worker
    worker_deps = AgentDependencies(
        agent_name=worker_name, 
        db_pool=ctx.deps.db_pool
    )
    
    try:
        # Await the sub-agent run recursively within the tool execution
        result = await worker.run(task_description, deps=worker_deps)
        logfire.info(f"Router received response from {worker_name}")
        return result.output
    except Exception as e:
        logfire.error(f"Worker {worker_name} failed: {e}")
        return f"Error executing worker '{worker_name}': {e}"
