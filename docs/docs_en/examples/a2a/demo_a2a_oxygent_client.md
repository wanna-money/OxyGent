# A2A OxyGent Client (Non-Streaming)

**Source:** `examples/a2a/demo_a2a_oxygent_client.py`

## Overview

This example demonstrates how to use OxyGent's built-in `A2AClientAgent` to send a non-streaming message to an A2A server and retrieve the task result. It creates a lightweight MAS containing only the A2A client agent, sends a single query, prints the response, and then fetches the completed task via `get_task`.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME` (required by the server, not the client itself)
- Start the A2A server first: `PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## How to Run

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_client.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL = "http://127.0.0.1:8090/a2a"` -- points to the OxyGent A2A server started by `demo_a2a_oxygent_server.py`.
- `Config.set_app_name("demo-a2a-oxygent-client")` -- sets the application name for logging and tracing.

### Components (`oxy_space`)

A single component is registered:

- **`A2AClientAgent.minimal()`** -- A factory method that creates a minimal A2A client agent with:
  - `name="a2a_client"` -- the agent's identifier within the MAS.
  - `server_url=SERVER_URL` -- the A2A server endpoint.
  - `timeout=60` -- HTTP request timeout in seconds.
  - `streaming=False` -- uses synchronous `message/send` rather than `message/stream`.
  - `enable_task_polling=False` -- does not automatically poll for task completion.

### Helper Function: `call_once`

The `call_once` function constructs an `OxyRequest` and dispatches it to the `a2a_client` agent. It accepts optional parameters for multi-turn conversations:

- `context_id` -- identifies a conversation session on the A2A server.
- `task_id` -- references a specific prior task.
- `reference_task_ids` -- list of prior task IDs for follow-up context.

The request sets `is_send_message=False` and `is_save_history=False` to avoid triggering the MAS's internal messaging and history persistence, since this is a client-only MAS.

### Entry Point

The `main()` coroutine:

1. Creates a MAS with only the A2A client agent.
2. Sends a query ("1+1 equals what?" in Chinese) via `call_once`.
3. Extracts and prints the response text and session metadata (`context_id`, `task_id`).
4. If a `task_id` was returned, calls `client.get_task(task_id)` to fetch the full task object from the server and prints it as formatted JSON.

## Key Concepts

- **`A2AClientAgent.minimal()`**: A convenience factory that creates a client agent without needing a full agent configuration. It handles agent card resolution, message formatting, and response parsing internally.
- **`OxyRequest` arguments**: The `query` key in `arguments` is the primary user message. Additional keys (`context_id`, `task_id`, `reference_task_ids`) enable multi-turn conversation tracking.
- **`get_task`**: Retrieves the current state of a task from the A2A server, useful for verifying task completion or inspecting artifacts.

## Expected Behavior

When run (with the server already started):

1. Sends the query to the A2A server and receives an LLM-generated answer (e.g., "1+1=2").
2. Prints the response text.
3. Prints the session identifiers (`context_id` and `task_id`).
4. Fetches and prints the full task JSON from the server, showing task status, artifacts, and metadata.
