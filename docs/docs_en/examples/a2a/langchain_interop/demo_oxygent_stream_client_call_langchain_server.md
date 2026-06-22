# OxyGent Streaming Client Calling LangChain A2A Server

**Source:** `examples/a2a/langchain_interop/demo_oxygent_stream_client_call_langchain_server.py`

## Overview

This example uses OxyGent's `A2AClientAgent` in streaming mode to call the LangChain A2A server. Unlike the non-streaming variant, this client uses the `message/stream` A2A method and consumes Server-Sent Events (SSE) from the server. It demonstrates how OxyGent handles streaming A2A responses transparently through the same `A2AClientAgent` interface.

## Prerequisites

- Python 3.10+
- OxyGent installed (`pip install -r requirements.txt`)
- **The LangChain A2A server must be running first:**
  ```bash
  PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_a2a_server.py
  ```

## How to Run

```bash
PYTHONPATH=. python examples/a2a/langchain_interop/demo_oxygent_stream_client_call_langchain_server.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL` is set to `http://127.0.0.1:8101/a2a`.
- `CLIENT_NAME` is `"langchain_stream_client"`, the Oxy name for this agent instance.

### Components

**`A2AClientAgent.minimal(...)`** -- Configured with:
- `streaming=True` -- uses the `message/stream` SSE method instead of `message/send`.
- `timeout=120` -- longer timeout to accommodate streaming.
- `enable_task_polling=False` -- not needed since the stream itself delivers the final result.

**`call_once(mas, query)`** -- Simplified helper (no multi-turn session parameters) that builds an `OxyRequest` and executes it.

### Entry Point

The `main()` coroutine:
1. Sets the app name to `"demo-oxygent-stream-client-call-langchain-server"`.
2. Creates an `oxy_space` with a single streaming `A2AClientAgent`.
3. Opens a `MAS` context and sends one query asking the server to describe its capabilities.
4. Prints the final aggregated response and session identifiers.

## Key Concepts

- **Streaming A2A**: The `message/stream` method returns results progressively as SSE events. The `A2AClientAgent` consumes these events and aggregates them into the final `OxyResponse`.
- **Same Interface, Different Transport**: Switching from non-streaming to streaming only requires changing `streaming=True` -- the rest of the OxyGent code remains identical.
- **No Task Polling Needed**: When streaming, the server sends the complete result through the event stream, so task polling is unnecessary.

## Expected Behavior

The client sends a query and receives a streaming response from the LangChain server. The console shows:
- `[final]` -- the fully assembled response text (e.g., `[LangChain Server] <query text>`).
- `session:` -- the `context_id` and `task_id` from the streaming session.

The response arrives after the SSE stream completes, with the server having emitted partial character-by-character updates.
