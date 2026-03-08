import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart, TextPart, ToolReturnPart
from agents.router import router_agent
from models.dependencies import RouterDependencies

def call_delegate_to_worker(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """
    Simulates the exact deterministic output of the Router LLM.
    Basically we are replacing the LLM with this function to decide which tool to call, and manually writing the routing logic below
    and create the response.
    """
    if len(messages) == 1:
        # Here we are saing that the "model" wants to call a tool. In ToolCallPart, we specify the tool to call and the arguements.
        # If the function signature changes, we will get a validation error.
        tool_call = ToolCallPart(tool_name='delegate_to_worker', args={"worker_name": "pm", "task_description": "draft roadmap"})
        return ModelResponse(parts=[tool_call])
    else:
        # To simulate that the tool has been executed, and the "model" synthezises the final answer
        return ModelResponse(parts=[TextPart("Delegation complete.")])

@pytest.mark.asyncio
async def test_router_delegation_contract():
    """
    Simulates the LLM reasoning to ensure the `router_agent` reacts correctly 
    when the router LLM decides to trigger the `delegate_to_worker` tool.
    """
    # Create a mock agent with a fixed response using TestModel
    test_model = TestModel()
    test_model.custom_output_text = "Mock PM finished drafting roadmap."
    mock_pm_agent = Agent(model=test_model)
    
    # Mock the dependency for the router agent
    mock_registry = {"pm": mock_pm_agent}
    deps = RouterDependencies(worker_registry=mock_registry, db_pool=None)
    
    # We replace the LLM model for the router agent with our deterministic FunctionModel
    with router_agent.override(model=FunctionModel(call_delegate_to_worker)):
        
        result = await router_agent.run("Ask the PM to draft a roadmap", deps=deps)        
        messages = result.all_messages()
        
        # Find the ModelResponse message which contains the ToolCalls
        tool_calls = [
            part for msg in messages if isinstance(msg, ModelResponse)
            for part in msg.parts if isinstance(part, ToolCallPart)
        ]
        
        assert len(tool_calls) > 0
        assert tool_calls[0].tool_name == "delegate_to_worker"
        
        # Assert the input to the tool call
        assert tool_calls[0].args == {"worker_name": "pm", "task_description": "draft roadmap"}

        # Assert the output of the tool call matches the test model
        tool_returns = [
            part for msg in messages if hasattr(msg, 'parts')
            for part in msg.parts if isinstance(part, ToolReturnPart)
        ]
        assert len(tool_returns) > 0
        assert tool_returns[0].tool_name == "delegate_to_worker"
        assert tool_returns[0].content == "Mock PM finished drafting roadmap."
