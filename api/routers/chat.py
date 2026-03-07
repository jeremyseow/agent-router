import logfire
from fastapi import APIRouter, HTTPException, Request
from models.api import ChatRequest, ChatResponse
from agents.router import router_agent
from models.dependencies import RouterDependencies

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, request: Request):
    """Conversational endpoint that channels exactly into the Router LLM. Target delegation logic is handled securely internally by the Pydantic AI tool loops."""
    logfire.info(f"Received chat request: session_id={req.session_id}")
    
    # Inject application dependencies from FastAPI state
    pool = request.app.state.pool
    worker_registry = request.app.state.worker_registry
    
    try:
        # 1. Provide Context mapping to the Router Agent
        router_deps = RouterDependencies(
            worker_registry=worker_registry, 
            db_pool=pool
        )
        
        # 2. Start the recursive interaction cycle.
        #    The LLM may call zero tools, one tool, or parallel tools sequentially before resolving.
        router_result = await router_agent.run(req.message, deps=router_deps)
        
        return ChatResponse(
            response=router_result.output,
            agent_used="router"
        )
            
    except Exception as e:
        logfire.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
