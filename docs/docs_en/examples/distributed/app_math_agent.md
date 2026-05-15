# Distributed Math Agent Service

**Source:** `examples/distributed/app_math_agent.py`

## Overview

This file defines the **math agent service**, the middle tier in a three-service distributed system. It runs on port 8081 and exposes a `WorkflowAgent` that handles pi-calculation requests through a custom Python workflow function. It also demonstrates cross-service agent communication by calling a remote time agent on port 8082 via SSE before performing the calculation. This service is called by the master agent on port 8080.

## Prerequisites

- Environment variables (in `.env` or exported):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider.
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM endpoint.
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier.
- **uv** must be installed (used to run the MCP math tools server).
- **The time agent service** (`app_time_agent.py`) must already be running on `http://127.0.0.1:8082` before starting this service.

### Startup Order

1. **Port 8082** -- Start `app_time_agent.py` first.
2. **Port 8081** -- Start this math agent second.
3. **Port 8080** -- Start `app_master_agent.py` last (optional, if you want the full distributed demo).

## How to Run

```bash
# Terminal 1 (start time agent first)
python -m examples.distributed.app_time_agent

# Terminal 2
python -m examples.distributed.app_math_agent
```

The service will be available at `http://127.0.0.1:8081`. It also starts a web UI at that address for standalone testing.

## Code Walkthrough

### Configuration

```python
Config.set_app_name("app-math")
Config.set_server_port(8081)
```

The service is given a distinct app name (`app-math`) and bound to port **8081** so it can coexist with the master agent on port 8080 and the time agent on port 8082.

### Components (`oxy_space`)

| Component | Type | Purpose |
|---|---|---|
| `default_name` | `HttpLLM` | Shared LLM backend. |
| `math_tools` | `StdioMCPClient` | Runs `mcp_servers/math_tools.py` via `uv`. Exposes two tools: `power` (exponentiation) and `calc_pi` (pi to N decimal places). |
| `time_agent` | `SSEOxyGent` | Remote proxy to the time agent service on port 8082. |
| `math_agent` | `WorkflowAgent` | The master agent for this service (`is_master=True`). Uses a custom `func_workflow` instead of LLM-driven reasoning. Has access to `math_tools` and `time_agent` as sub-agents. |

### Workflow Function

The `workflow` function is the core logic:

```python
async def workflow(oxy_request: OxyRequest):
```

It performs the following steps:

1. **Reads conversation history** -- Calls `oxy_request.get_short_memory()` for the local agent's history and `oxy_request.get_short_memory(master_level=True)` for the top-level user conversation.
2. **Calls the time agent** -- Sends "What time is it now?" to the remote `time_agent` on port 8082 via `oxy_request.call()`. This demonstrates cross-service communication.
3. **Extracts the precision parameter** -- Uses a regex to find digits in the user query (e.g., "30" from "The 30 positions of pi").
4. **Calls `calc_pi`** -- If a number is found, calls the `calc_pi` MCP tool with that precision.
5. **Returns a fallback** -- If no number is found, returns a default 2-digit approximation (3.14).

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="The 30 positions of pi")
```

Starts the web service on port 8081 with a demo query for standalone testing.

## Key Concepts

- **WorkflowAgent** -- Unlike `ReActAgent` (which uses LLM reasoning loops), a `WorkflowAgent` executes a deterministic Python function (`func_workflow`). This gives developers full control over the execution flow while still leveraging sub-agents and tools.
- **oxy_request.call()** -- The mechanism for one agent to invoke another (local or remote). The `callee` parameter names the target, and `arguments` passes the payload. This works transparently across process boundaries when the callee is an `SSEOxyGent`.
- **master_level=True** -- When accessing conversation history or the user query, `master_level=True` retrieves the context from the top-level master agent rather than the current agent. This is essential in distributed setups where the math agent needs to see what the end user originally asked.
- **Cross-service tracing** -- Each request carries a `trace_id` that links the entire distributed call chain for debugging and observability.

## Expected Behavior

1. When the master agent on port 8080 sends a pi-calculation request, it arrives at this service via SSE.
2. The `workflow` function first queries the time agent on port 8082 and prints the current time.
3. It then extracts the number of decimal places from the query and calls the `calc_pi` MCP tool.
4. The computed pi value is returned to the calling master agent, which displays it to the user.
5. Console output will show the conversation history, the user's original query, and the current time fetched from the remote time agent.
