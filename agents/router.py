from pydantic_ai import Agent, RunContext
from core.config import settings
from core.constants import ROUTER_MODEL
import os
import logfire
from models.dependencies import RouterDependencies, AgentDependencies

# We removed output_type structured constraints so the router can converse freely
router_agent = Agent(
    ROUTER_MODEL,
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
        "You are the main Supervising Orchestrator. Your primary job is to coordinate specialized Worker Agents.\n"
        "### SPECIAL INSTRUCTIONS:\n"
        "1. **Never Guess**: Do not rely on your own internal training data for technical or complex questions. Instead, ALWAYS search the knowledge base.\n"
        "2. **Delegate Aggressively**: If a task falls squarely within the role of a specialized worker (e.g., coding -> engineer, research -> research_assistant, project knowledge -> librarian), you MUST invoke the `delegate_to_worker` tool.\n"
        "3. **Be Specific**: When delegating, be specific about what you want the worker to do. Do not just say 'do research'. Say 'research the best way to implement X'.\n"
        "4. **Concurrency: You can call the delegate_to_worker tool multiple times in parallel for different tasks if there are no dependencies between them. Else, you can take the output of a task and use it as input for another task.\n"
        "5. **Synthesize**: Once workers return their results, summarize and present them to the user concisely.\n\n"
        "Available Specialized Workers:\n"
        f"{agent_descriptions}\n\n"
        "If the user asks a simple greeting or general question not related to the project, answer directly."
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
