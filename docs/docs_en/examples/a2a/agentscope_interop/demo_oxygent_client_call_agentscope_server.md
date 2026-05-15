# OxyGent Client Calling AgentScope A2A Server

**Source:** `examples/a2a/agentscope_interop/demo_oxygent_client_call_agentscope_server.py`

## Overview

This example uses OxyGent's built-in `A2AClientAgent` to call a remote AgentScope A2A server. It demonstrates the streaming A2A path (`message/stream`) with the AgentScope server's `TaskStatusUpdateEvent`-based streaming handler. The `A2AClientAgent` automatically discovers the agent card, sends the request, and aggregates the streaming response into a final `OxyResponse`.

## Prerequisites

- Python 3.10+
- OxyGent installed (`pip install -r requirements.txt`)
- **The AgentScope A2A server must be running first:**
  ```bash
  PYTHONPATH=. python examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py
  ```

## How to Run

```bash
PYTHONPATH=. python examples/a2a/agentscope_interop/demo_oxygent_client_call_agentscope_server.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL` is set to `http://127.0.0.1:8003`, matching the AgentScope server's address.
- `Config.set_app_name(...)` sets the application identifier for logging.

### Components

**`A2AClientAgent.minimal(...)`** -- Creates a minimal A2A client agent with:
- `name="agentscope_client"` -- the Oxy name used for routing within MAS.
- `server_url` -- the AgentScope server's base URL. The agent card path (`.well-known/agent.json`) is appended automatically by default.
- `streaming=True` -- uses the `message/stream` method, matching the AgentScope server's stream handler.
- `timeout=120` -- 120-second HTTP timeout for streaming.
- `enable_task_polling=False` -- not needed since the stream delivers the final result.
- `task_poll_interval_seconds=1` and `task_poll_max_wait_seconds=30` -- polling parameters (unused when streaming, but configured as fallback).

**`call_once(mas, query, context_id, task_id)`** -- Helper that builds an `OxyRequest` targeting the `agentscope_client` agent and executes it. Optional `context_id` and `task_id` support multi-turn sessions.

### Entry Point

The `main()` coroutine:
1. Sets the app name.
2. Creates the `oxy_space` with a single streaming `A2AClientAgent`.
3. Opens a `MAS` async context manager.
4. Sends one query asking the AgentScope server to introduce itself in one sentence.
5. Prints the response output and session identifiers (`context_id`, `task_id`).

## Key Concepts

- **A2AClientAgent with AgentScope**: The same `A2AClientAgent` class works with any A2A-compliant server, whether built with LangChain, LangGraph, AgentScope, or any other framework.
- **Automatic Agent Card Discovery**: The client fetches `.well-known/agent.json` from the server URL to learn about capabilities before sending messages.
- **Streaming with A2A SDK Server**: The AgentScope server uses the official `a2a` SDK's `A2AStarletteApplication` which handles SSE streaming differently from the manual FastAPI implementations -- the `A2AClientAgent` handles both transparently.
- **Session Metadata**: The response includes `context_id` and `task_id` that can be reused for multi-turn conversations.

## Expected Behavior

The client sends a query and receives a streaming response from the AgentScope server. Console output shows:
- `[turn1]` -- the aggregated response text from the AgentScope server, which will be in the format: "I am the AgentScope A2A test service. I have received your question: <input>. This is a streaming demo response." (in Chinese).
- `session:` -- the `context_id` and `task_id` from the session, which could be used for follow-up turns.
