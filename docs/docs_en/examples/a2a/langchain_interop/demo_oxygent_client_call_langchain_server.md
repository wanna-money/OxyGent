# OxyGent Client Calling LangChain A2A Server

**Source:** `examples/a2a/langchain_interop/demo_oxygent_client_call_langchain_server.py`

## Overview

This example uses OxyGent's built-in `A2AClientAgent` to call a remote LangChain A2A server. It demonstrates the standard OxyGent pattern for consuming any A2A-compliant service: configure an `A2AClientAgent`, register it in a `MAS`, and execute requests through the MAS runtime. The communication uses the non-streaming `message/send` path with task polling enabled.

## Prerequisites

- Python 3.10+
- OxyGent installed (`pip install -r requirements.txt`)
- **The LangChain A2A server must be running first:**
  ```bash
  PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_a2a_server.py
  ```

## How to Run

```bash
PYTHONPATH=. python examples/a2a/langchain_interop/demo_oxygent_client_call_langchain_server.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL` is set to `http://127.0.0.1:8101/a2a`, matching the LangChain server's address.
- `Config.set_app_name(...)` sets the application identifier for logging and tracing.

### Components

**`A2AClientAgent.minimal(...)`** -- Creates a minimal A2A client agent with:
- `name="langchain_client"` -- the Oxy name used for routing within MAS.
- `server_url` -- the LangChain server's A2A endpoint.
- `streaming=False` -- uses the `message/send` (synchronous) method.
- `enable_task_polling=True` -- after sending, polls `tasks/get` until the task reaches a terminal state.
- `timeout=60` -- 60-second HTTP timeout.

**`call_once(mas, query, context_id, task_id)`** -- Helper that builds an `OxyRequest` targeting the `langchain_client` agent and executes it through the MAS. Optional `context_id` and `task_id` parameters support multi-turn sessions.

### Entry Point

The `main()` coroutine:
1. Sets the app name.
2. Creates the `oxy_space` with a single `A2AClientAgent`.
3. Opens a `MAS` async context manager.
4. Sends one query asking the server to introduce itself and identify its framework.
5. Prints the response output and session identifiers (`context_id`, `task_id`).

## Key Concepts

- **A2AClientAgent**: OxyGent's built-in component for calling any A2A-compliant server. Handles agent card discovery, message formatting, and task lifecycle automatically.
- **MAS as Runtime**: Even for a single outbound call, the agent is registered in a `MAS` instance, which manages the Oxy lifecycle (init, execute, teardown).
- **Task Polling**: With `enable_task_polling=True`, the client can handle servers that return tasks in a `working` state and require polling for completion.
- **Non-Streaming A2A**: Uses `message/send` for a simple request-response interaction.

## Expected Behavior

The client sends a Chinese query asking the server to introduce itself. The console output shows:
- `[turn1]` -- the server's response, which will be `[LangChain Server] <query text>` since the demo server echoes input.
- `session:` -- the `context_id` and `task_id` returned by the server, which could be used for follow-up turns.
