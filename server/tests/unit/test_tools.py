import os
import pytest
from tools.fs_tools import read_file, write_file, AGENT_OUTPUT_DIR
from models.dependencies import AgentDependencies

class MockRunContext:
    """A dummy Pydantic AI RunContext to bypass complex LLM dependency injection during unit testing."""
    def __init__(self, deps=None):
        self.deps = deps

@pytest.mark.asyncio
async def test_read_file_error():
    """Verifies that missing files return the correct error string rather than crashing the LLM."""
    ctx = MockRunContext(deps=None)
    result = await read_file(ctx, "does_not_exist_file.txt")
    assert "Error reading file" in result

@pytest.mark.asyncio
async def test_write_file_directory_traversal():
    """
    Verifies the tool's sandbox correctly strips directory traversal payloads 
    and forces the output directly into the `AGENT_OUTPUT_DIR`.
    """
    ctx = MockRunContext(deps=None)
    
    # Act: Attempt to hack the system by writing backwards
    traversal_path = "../../../etc/passwd"
    content = "malicious payload"
    
    result = await write_file(ctx, traversal_path, content)
    
    # Assert
    assert "Error: Directory traversal blocked" in result
