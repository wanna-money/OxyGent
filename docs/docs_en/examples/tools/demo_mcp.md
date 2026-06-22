# MCP Tool Integration Demo

**Source:** `examples/tools/demo_mcp.py`

## Overview

This example shows how to integrate external tools via the Model Context Protocol (MCP) using `StdioMCPClient`. Three different MCP tool servers are configured -- a time server, a map server, and a math server -- illustrating how OxyGent can connect to any MCP-compliant tool process. The example also includes commented-out configurations for `SSEMCPClient` and `StreamableMCPClient`, demonstrating alternative transport modes.

## Prerequisites

- Environment variables (set in `.env` or shell):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM API
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier
- **Node.js** installed (required for `npx`-based MCP servers like the map tools)
- **uv** or **uvx** installed (required for Python-based MCP servers like the time and math tools)
- For the map tools: a valid AMap (Gaode) Maps API key (replace `"API_KEY"` in the code)
- The `mcp_servers/` directory must contain `math_tools.py` for the math MCP server

## How to Run

```bash
python -m examples.tools.demo_mcp
```

## Code Walkthrough

### Configuration

An `HttpLLM` named `"default_llm"` is configured from environment variables. This LLM powers the reasoning of the ReAct agent.

### Components (`oxy_space`)

The `oxy_space` contains five components (two commented out):

1. **`HttpLLM("default_llm")`** -- The language model.
2. **`StdioMCPClient("time_tools")`** -- Launches the `mcp-server-time` package via `uvx` with the timezone set to `Asia/Shanghai`. Communicates over stdio.
3. **`StdioMCPClient("map_tools")`** -- Launches the `@amap/amap-maps-mcp-server` package via `npx`. Requires an AMap API key passed through the `env` parameter.
4. **`StdioMCPClient("math_tools")`** -- Runs a local Python MCP server (`mcp_servers/math_tools.py`) via `uv`. Provides mathematical computation tools.
5. **`ReActAgent("master_agent")`** -- A ReAct agent wired to `"time_tools"` and `"math_tools"`. It uses `"default_llm"` for reasoning (set explicitly via `llm_model`).

The commented-out sections show how to use:
- **`SSEMCPClient`** -- Connects to a remote MCP server via Server-Sent Events at a given URL.
- **`StreamableMCPClient`** -- Connects to a remote MCP server via a streamable HTTP endpoint.

### Entry Point

The `main()` coroutine creates a `MAS` context, which initializes all MCP client connections (spawning the stdio subprocesses), and then starts the web service with the initial query `"What time is it"`.

## Key Concepts

- **StdioMCPClient** -- Spawns an external process and communicates via stdin/stdout using the MCP protocol. The `params` dict specifies the `command`, `args`, and optional `env` for the subprocess.
- **SSEMCPClient** -- Connects to a running MCP server over HTTP using Server-Sent Events. Useful for remote or shared tool servers.
- **StreamableMCPClient** -- Similar to SSE but uses a streamable HTTP endpoint (`/mcp`). Suitable for bidirectional streaming.
- **MCP (Model Context Protocol)** -- A standardized protocol for LLM tool integration that allows agents to discover and invoke tools from any MCP-compliant server.
- **Tool name referencing** -- Agents reference tools by the `name` given to the MCP client (e.g., `"time_tools"`). The MAS runtime resolves these names to the actual tool instances.

## Expected Behavior

1. The MAS initializes and spawns the `time_tools` and `math_tools` MCP server processes (and optionally `map_tools`).
2. The web server starts at `http://127.0.0.1:8080`.
3. The agent receives the query "What time is it".
4. The agent reasons that it needs to use the time tool, calls it via MCP, and receives the current time in the `Asia/Shanghai` timezone.
5. The agent presents the time to the user in the web UI.
