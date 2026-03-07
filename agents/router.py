from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from core.config import settings
import os
from models.dependencies import RouterDependencies

# Pydantic AI's Gemini integration looks for GOOGLE_API_KEY
if settings.gemini_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.gemini_api_key

class RouterResponse(BaseModel):
    should_delegate: bool
    target_agent: str = "none" # Use dynamic string referencing instead of fixed literals mapping to db registry keys
    final_response: str

router_agent = Agent(
    'gemini-2.5-flash',
    output_type=RouterResponse,
    deps_type=RouterDependencies,
    defer_model_check=True
)

@router_agent.system_prompt
async def get_system_prompt(ctx: RunContext[RouterDependencies]) -> str:
    agents_list = ", ".join(ctx.deps.available_agents) if ctx.deps.available_agents else "none"
    return (
        "You are the main Router Agent. Your job is to analyze the user's request and decide whether "
        f"to answer it yourself or delegate to a specialized worker agent (Available targets: {agents_list}).\n"
        "If you can answer it yourself or it's a general conversation, set should_delegate=False and provide final_response.\n"
        "If you need to delegate, identify the target_agent EXACTLY as listed above, and explain the task in final_response, which will be passed to the target agent."
    )
