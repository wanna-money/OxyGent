# MCP Tool with Custom Headers Demo

**Source:** `examples/tools/demo_mcp_with_headers.py`

## Overview

This example demonstrates three different strategies for passing custom HTTP headers to a remote MCP tool server via `StreamableMCPClient`. Headers can be specified statically on the client, dynamically via `shared_data`, or inherited from the frontend request. The example runs three separate MAS instances to illustrate each approach and explains the priority order when multiple header sources overlap.

## Prerequisites

- Environment variables (set in `.env` or shell):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM API
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier
- A running MCP server at `http://127.0.0.1:8000/mcp` that accepts HTTP headers (e.g., a `StreamableMCPClient`-compatible server with a `power` tool)

## How to Run

```bash
python -m examples.tools.demo_mcp_with_headers
```

## Code Walkthrough

### Configuration

Three separate `oxy_space` configurations are defined to demonstrate each header-passing strategy.

### Components (`oxy_space`)

#### `oxy_space1` -- Static Headers

```python
oxy.StreamableMCPClient(
    name="time_tools",
    server_url="http://127.0.0.1:8000/mcp",
    headers={"key1": "value1"},
)
```

Headers are set directly on the `StreamableMCPClient`. Every MCP call from this client will include `{"key1": "value1"}` in the HTTP request headers.

#### `oxy_space2` -- Dynamic Headers via `shared_data`

```python
oxy.StreamableMCPClient(
    name="time_tools",
    server_url="http://127.0.0.1:8000/mcp",
    headers={"key1": "value1"},
    is_dynamic_headers=True,
)
```

When `is_dynamic_headers=True`, the client reads additional headers from the `shared_data["headers"]` field of the `OxyRequest` at call time. In this example, `{"key2": "value2"}` is passed via the payload's `shared_data`.

#### `oxy_space3` -- Inherited Frontend Headers

```python
oxy.StreamableMCPClient(
    name="time_tools",
    server_url="http://127.0.0.1:8000/mcp",
    headers={"key1": "value1"},
    is_dynamic_headers=True,
    is_inherit_headers=True,
)
```

When `is_inherit_headers=True`, the client additionally forwards headers from the original frontend HTTP request (e.g., browser or API client) to the MCP server. This is useful for propagating authentication tokens or session identifiers.

### Entry Point

The `main()` coroutine runs three MAS instances sequentially:

1. **Static headers** -- Calls the `power` tool directly via `mas.call()` with static headers.
2. **Dynamic headers** -- Uses `mas.chat_with_agent()` with a payload containing `shared_data.headers`.
3. **Inherited headers** -- Starts a web service so that frontend request headers are available for forwarding.

## Key Concepts

- **Static headers** (`headers` parameter) -- Fixed headers configured at client instantiation time. Always sent with every MCP request.
- **Dynamic headers** (`is_dynamic_headers=True`) -- Headers read from `shared_data["headers"]` in the request payload at runtime. Allows per-request header customization.
- **Inherited headers** (`is_inherit_headers=True`) -- Headers transparently forwarded from the original frontend HTTP request to the MCP server. Enables header pass-through for auth tokens, tracing IDs, etc.
- **Header priority order** -- When headers from multiple sources share the same key, the priority is: **frontend request headers > `shared_data` headers > static client headers**. Higher-priority sources override lower-priority ones.
- **`mas.call()`** -- Directly invokes a named Oxy component (tool or LLM) without going through an agent's reasoning loop. Useful for scripting and testing.

## Expected Behavior

1. **First MAS** (`oxy_space1`): Directly calls the `power` tool with `n=2, m=3`, sending `{"key1": "value1"}` as headers. The tool computes 2^3 = 8.
2. **Second MAS** (`oxy_space2`): The agent processes the query "2 to the power of 3" with dynamic headers `{"key2": "value2"}` merged with the static `{"key1": "value1"}`.
3. **Third MAS** (`oxy_space3`): A web service starts, and any frontend request headers are forwarded along with the static and dynamic headers when the agent calls MCP tools.
