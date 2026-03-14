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
        "### SPECIAL INSTRUCTIONS:\n"
        "1. **Prioritize the Knowledge Base**: You have direct access to the `search_knowledge_base` tool. Before asking any other agents on technical or complex questions, consider using this tool yourself.\n"
        "2. **Delegate Aggressively**: If a task requires active execution (coding, research assistant tasks, complex analysis), delegate to the specialized workers.\n"
        "3. **Concurrency**: If tasks have no dependencies on each other, delegate to multiple workers in parallel. Else, you can delegate to them sequentially, with the output of 1 agent as input to the next agent.\n"
        "4. **Be Specific**: When delegating, be specific about what you want the worker to do.\n"
        "5. **Synthesis**: Once workers return their results, summarize and present them to the user concisely.\n\n"
        "### FEW-SHOT EXAMPLES:\n"
        "User: 'How do I design an event-driven system?'\n"
        "Action: Call `search_knowledge_base(query='event-driven system design')`\n\n"
        "User: 'Write a python script to test the chat API.'\n"
        "Action: Call `search_knowledge_base(query='chat API specification')` -> then delegate to `engineer` to write the script.\n\n"
        "User: 'What is the financial outlook of Company A?'\n"
        "Action: Call `search_knowledge_base(query='Company A financial outlook')` -> then delegate to multiple `research_assistant` in parallel to get the latest information on various domains -> then delegate to `financial_analyst` to analyze the research results.\n\n"
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
    Searches the internal knowledge base for technical documentation and project specifications.
    Use this tool to answer questions about project architecture, design decisions, API specifications, 
    database schemas, and any other technical details documented in the knowledge base.
    """
    return await search_knowledge_base(ctx, query)
