# OxyGent Client Calling LangGraph A2A Server

**Source:** `examples/a2a/langgraph_interop/demo_oxygent_client_call_langgraph_server.py`

## Overview

This example uses OxyGent's built-in `A2AClientAgent` to call a remote LangGraph A2A server. It demonstrates multi-turn conversation support: after the first query, the response's `context_id` and `task_id` are passed into a second call, maintaining session continuity across the A2A protocol. The communication uses the non-streaming `message/send` path with task polling enabled.

## Prerequisites

- Python 3.10+
- OxyGent installed (`pip install -r requirements.txt`)
- **The LangGraph A2A server must be running first:**
  ```bash
  PYTHONPATH=. python examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py
  ```

## How to Run

```bash
PYTHONPATH=. python examples/a2a/langgraph_interop/demo_oxygent_client_call_langgraph_server.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL` is set to `http://127.0.0.1:8102/a2a`, matching the LangGraph server's address.
- `Config.set_app_name(...)` sets the application identifier.

### Components

**`A2AClientAgent.minimal(...)`** -- Creates a minimal A2A client agent with:
- `name="langgraph_client"` -- the Oxy name used for routing within MAS.
- `server_url` -- the LangGraph server's A2A endpoint.
- `streaming=False` -- uses the `message/send` method.
- `enable_task_polling=True` -- polls `tasks/get` until the task completes.
- `timeout=60` -- 60-second HTTP timeout.

**`call_once(mas, query, context_id, task_id)`** -- Helper that builds an `OxyRequest` targeting the `langgraph_client` agent and executes it. Optional `context_id` and `task_id` parameters enable multi-turn sessions.

### Entry Point

The `main()` coroutine:
1. Sets the app name.
2. Creates the `oxy_space` with a single `A2AClientAgent`.
3. Opens a `MAS` async context manager.
4. **Turn 1**: Sends a query asking the server to introduce itself and its framework.
5. **Turn 2**: Sends a follow-up query using the `context_id` and `task_id` from turn 1, asking the server to summarize the previous answer.
6. Prints each response and session identifiers.

## Key Concepts

- **Multi-Turn A2A Sessions**: By passing `context_id` and `task_id` from one response to the next request, the client maintains conversational context across the A2A protocol boundary.
- **A2AClientAgent**: OxyGent's built-in component for consuming any A2A server. Handles agent card discovery, message formatting, and task lifecycle.
- **Task Polling**: With `enable_task_polling=True`, the client handles servers that may return intermediate `working` states before completion.
- **MAS Lifecycle**: The `async with MAS(...)` pattern ensures proper initialization and cleanup of all registered Oxy components.

## Expected Behavior

The client performs two conversation turns against the LangGraph server. Console output shows:

- `[turn1]` -- the server's response to the first query (e.g., `[LangGraph Server] <query text>`).
- `session:` -- the `context_id` and `task_id` from turn 1.
- `[turn2]` -- the server's response to the follow-up query, with the same session context.
- `session:` -- the session identifiers from turn 2.

Since the demo server simply echoes input, the turn 2 response will echo the follow-up question rather than actually summarizing turn 1.
