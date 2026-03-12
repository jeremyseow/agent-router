import logfire
from fastapi import APIRouter, HTTPException, Request
from models.api import ChatRequest, ChatResponse
from agents.router import router_agent
from agents.summarizer import summarizer_agent
from models.dependencies import RouterDependencies
from db.context import load_chat_session, save_chat_session
from pydantic_ai.messages import ModelRequest, UserPromptPart, ModelResponse, TextPart
from pydantic_ai.messages import ModelMessagesTypeAdapter

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, request: Request):
    """Conversational endpoint that channels exactly into the Router LLM. Target delegation logic is handled securely internally by the Pydantic AI tool loops."""
    logfire.info(f"Received chat request: session_id={req.session_id}")
    
    # Inject application dependencies from FastAPI state
    pool = request.app.state.pool
    worker_registry = request.app.state.worker_registry
    
    try:
        # Provide Context mapping to the Router Agent
        router_deps = RouterDependencies(
            worker_registry=worker_registry, 
            db_pool=pool
        )
        
        # Load the persistent conversational memory (Summary string)
        summary = await load_chat_session(req.session_id, pool)
        
        message_history = []
        if summary:
            # We fulfill the user's specific request: structurally injecting the past summary directly into the AI agent's timeline
            message_history = [
                ModelRequest(parts=[UserPromptPart(content=f"Previous Conversation Summary:\n{summary}")]),
                ModelResponse(parts=[TextPart(content="Understood. I will use this summary as conversational context for our current ongoing interaction.")])
            ]
        
        # Start the recursive interaction cycle with the Router
        router_result = await router_agent.run(
            req.message, 
            deps=router_deps, 
            message_history=message_history
        )
        
        # Serialize the exhaustive interaction trace spanning the history and new router operations
        full_json_bytes = ModelMessagesTypeAdapter.dump_json(router_result.all_messages())
        
        # Execute the pure summarization agent on the payload
        logfire.info("Running Summarizer Agent on the conversation history...")
        summary_result = await summarizer_agent.run(
            f"Please summarize the following conversation history. It represents an ongoing interaction between a user and an AI router agent. Capture all crucial context, facts, decisions, and system statuses so it can be used as memory mapping for the next turn:\n\n{full_json_bytes.decode('utf-8')}"
        )
        
        # Save the updated summarized conversational memory back to PostgreSQL
        await save_chat_session(req.session_id, summary_result.output, pool)
        
        return ChatResponse(
            response=router_result.output,
            agent_used="router"
        )
            
    except Exception as e:
        logfire.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
