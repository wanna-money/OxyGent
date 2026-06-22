"""MCP tool implementations for OxyGent.

Provides MCP client transports (stdio, SSE, streamable-HTTP) and the
MCPTool proxy that exposes individual server tools to agents.
"""

from .mcp_tool import MCPTool
from .sse_mcp_client import SSEMCPClient
from .stdio_mcp_client import StdioMCPClient
from .streamable_mcp_client import StreamableMCPClient

__all__ = [
    "MCPTool",
    "StdioMCPClient",
    "SSEMCPClient",
    "StreamableMCPClient",
]
