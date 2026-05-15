# OxyGent Streaming Client Calling LangGraph A2A Server

**Source:** `examples/a2a/langgraph_interop/demo_oxygent_stream_client_call_langgraph_server.py`

## Overview

This example uses OxyGent's `A2AClientAgent` in streaming mode to call the LangGraph A2A server. It uses the `message/stream` A2A method and consumes Server-Sent Events from the server. This demonstrates the streaming variant of OxyGent-to-LangGraph interoperability, complementing the non-streaming example.

## Prerequisites

- Python 3.10+
- OxyGent installed (`pip install -r requirements.txt`)
- **The LangGraph A2A server must be running first:**
  ```bash
  PYTHONPATH=. python examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py
  ```

## How to Run

```bash
PYTHONPATH=. python examples/a2a/langgraph_interop/demo_oxygent_stream_client_call_langgraph_server.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL` is set to `http://127.0.0.1:8102/a2a`.
- `CLIENT_NAME` is `"langgraph_stream_client"`, the Oxy name for this agent instance.

### Components

**`A2AClientAgent.minimal(...)`** -- Configured with:
- `streaming=True` -- uses the `message/stream` SSE method.
- `timeout=120` -- longer timeout to accommodate streaming.
- `enable_task_polling=False` -- not needed since the stream delivers the final result.

**`call_once(mas, query)`** -- Simplified helper that builds an `OxyRequest` and executes it through MAS.

### Entry Point

The `main()` coroutine:
1. Sets the app name to `"demo-oxygent-stream-client-call-langgraph-server"`.
2. Creates an `oxy_space` with a single streaming `A2AClientAgent`.
3. Opens a `MAS` context and sends one query asking about LangGraph A2A capabilities.
4. Prints the final aggregated response and session identifiers.

## Key Concepts

- **Streaming A2A with LangGraph**: The LangGraph server's `message/stream` endpoint emits character-by-character SSE events, which the `A2AClientAgent` consumes and aggregates.
- **Minimal Code Change**: Compared to the non-streaming LangGraph client, only `streaming=True` and `enable_task_polling=False` differ -- the rest of the OxyGent code is identical.
- **Transparent Streaming**: The `A2AClientAgent` handles SSE parsing internally, presenting the final result as a standard `OxyResponse`.

## Expected Behavior

The client sends a query and receives a streaming response from the LangGraph server. Console output shows:
- `[final]` -- the fully assembled response text (e.g., `[LangGraph Server] <query text>`).
- `session:` -- the `context_id` and `task_id` from the streaming session.

The server emits partial updates character by character; the client aggregates them into the final output.
