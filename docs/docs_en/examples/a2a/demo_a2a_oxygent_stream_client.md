# A2A OxyGent Streaming Client

**Source:** `examples/a2a/demo_a2a_oxygent_stream_client.py`

## Overview

This example demonstrates OxyGent's streaming A2A client capability. It uses `A2AClientAgent` in streaming mode to send a message to the A2A server and receive the response incrementally via Server-Sent Events (SSE). After the stream completes, it also retrieves the final task state.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME` (required by the server)
- Start the A2A server first: `PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## How to Run

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_stream_client.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL = "http://127.0.0.1:8090/a2a"` -- the A2A server endpoint.
- `Config.set_app_name("demo-a2a-stream-client-agent")` -- sets the application name for logging.

### Components (`oxy_space`)

A single component:

- **`A2AClientAgent.minimal()`** with:
  - `name="stream_client"` -- agent identifier.
  - `server_url=SERVER_URL` -- target A2A server.
  - `streaming=True` -- enables SSE streaming via `message/stream` endpoint.
  - `timeout=120` -- longer timeout to accommodate streaming responses.
  - `enable_task_polling=False` -- no automatic background polling.

### Helper Function: `call_once`

Constructs an `OxyRequest` targeting the `stream_client` agent with the user query. The streaming behavior is handled internally by the `A2AClientAgent` -- the caller still awaits a single `OxyResponse`, but the agent processes SSE chunks internally and assembles the final output.

### Entry Point

The `main()` coroutine:

1. Creates a MAS with the streaming client agent.
2. Sends a query asking for a 100-character story (in Chinese).
3. Prints the final assembled response and session metadata.
4. Fetches and prints the complete task JSON via `get_task`.

## Key Concepts

- **Streaming vs. Non-Streaming**: When `streaming=True`, the `A2AClientAgent` uses the A2A `message/stream` endpoint, receiving incremental `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent` chunks via SSE. The agent internally accumulates these into the final response.
- **Timeout Considerations**: Streaming responses may take longer than synchronous ones, so the timeout is set to 120 seconds instead of 60.
- **Task Retrieval**: Even after streaming completes, `get_task` can be used to retrieve the finalized task state from the server.

## Expected Behavior

When run (with the server already started):

1. Sends the query to the A2A server via the streaming endpoint.
2. The `A2AClientAgent` receives SSE chunks internally and assembles the response.
3. Prints `[final]` followed by the complete response text (a short story).
4. Prints the session identifiers (`context_id` and `task_id`).
5. Fetches and prints the full task JSON showing `completed` state.
