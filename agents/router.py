from pydantic_ai import Agent, RunContext
from core.config import settings
from core.constants import ROUTER_MODEL
import os
import logfire
from models.dependencies import RouterDependencies, AgentDependencies
from tools.rag_tools import search_knowledge_base

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
        "You are the main Supervising Orchestrator. Your primary job is to coordinate specialized Worker Agents to help users with their tasks.\n"
        "### OPERATING PRINCIPLES:\n"
        "1. **Analyze First**: For any complex request, start by creating a mental 'Plan'. Think about which tools are needed and in what order.\n"
        "2. **Prioritize the Knowledge Base**: You have direct access to the `search_kb` tool. Before asking any other agents on technical or complex questions, consider using this tool itself to get foundational context or specifications.\n"
        "3. **Optimal Delegation**: \n"
        "   - **Parallel**: If tasks are independent (e.g., researching three different topics), call `delegate_to_worker` multiple times in parallel.\n"
        "   - **Sequential**: If a task depends on the output of a previous one (e.g., search spec -> write code), wait for the first worker to return before delegating to the next.\n"
        "4. **Synthesis**: Do not just repeat worker output. Summarize, compare, and integrate the results into a cohesive answer for the user.\n\n"
        "### FEW-SHOT EXAMPLES:\n"
        "User: 'How do I design an event-driven system?'\n"
        "Action: Call `search_kb(query='event-driven system design')`\n\n"
        "User: 'Research Company A's financial state and write a summary script.'\n"
        "Action: \n"
        "   1. Call `search_kb(query='Company A financial modeling data')` AND `delegate_to_worker(worker_name='research_assistant', task_description='latest news on Company A')` in parallel.\n"
        "   2. Once both return, call `delegate_to_worker(worker_name='engineer', task_description='Write a summary script based on: [KB_OUT] and [RESEARCH_OUT]')`.\n"
        "   3. Present the final script and summary to the user.\n\n"
        "### Available Specialized Workers:\n"
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

@router_agent.tool
async def search_kb(ctx: RunContext[RouterDependencies], query: str) -> str:
    """
    Searches the internal knowledge base for technical documentation across various domains (software engineering, 
    system design, financial modeling, etc.). Use this tool to retrieve foundational knowledge, 
    specifications, or architectural patterns stored in the knowledge base.
    """
    return await search_knowledge_base(ctx, query)
