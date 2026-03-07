from tools.fs_tools import read_file, write_file
from tools.api_tools import make_get_request, make_post_request
from pydantic_ai import WebSearchTool

# Map string identifiers from the database to actual Python tool functions
AVAILABLE_TOOLS = {
    "read_fs": read_file,
    "write_fs": write_file,
    "api_get": make_get_request,
    "api_post": make_post_request,
}

BUILTIN_TOOLS = {
    "web_search": WebSearchTool(),
}

