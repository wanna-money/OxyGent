# AgentScope A2A Server

**Source:** `examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py`

## Overview

This example launches an A2A-compliant server using AgentScope's official A2A SDK types and the `A2AStarletteApplication` builder. Unlike the LangChain and LangGraph server demos that manually implement JSON-RPC endpoints, this server uses the `a2a` Python package to handle protocol details. The server implements a streaming echo handler that acknowledges received input with a fixed response, emitting it character by character via A2A `TaskStatusUpdateEvent` events.

## Prerequisites

- Python 3.10+
- Extra packages: `pip install a2a agentscope uvicorn`
- No LLM API keys are required -- the server echoes input without calling any model.

## How to Run

```bash
PYTHONPATH=. python examples/a2a/agentscope_interop/demo_agentscope_a2a_server.py
```

The server starts at `http://127.0.0.1:8003`.

## Code Walkthrough

### Configuration

| Constant | Value | Purpose |
|---|---|---|
| `HOST` | `0.0.0.0` | Listen address (all interfaces) |
| `PORT` | `8003` | Listen port |
| `BASE_URL` | `http://127.0.0.1:8003` | Advertised URL in the Agent Card |

### Components

**`build_agent_card()`** -- Constructs an `AgentCard` using the official `a2a.types` Pydantic models. Declares capabilities including `streaming=True` and `state_transition_history=True`, and registers a single `chat` skill with AgentScope-related tags.

**`AgentScopeStreamHandler`** -- The core handler class. It implements the `on_message_send_stream` method, which is an async generator yielding A2A `Event` objects:
1. **Working event** -- Yields a `TaskStatusUpdateEvent` with state `working` to signal processing has started.
2. **Streaming content** -- Constructs a Chinese response string acknowledging the user's input, then yields one `TaskStatusUpdateEvent` per character with the progressively growing text in a `Message` object.
3. **Completed event** -- Yields a final `TaskStatusUpdateEvent` with state `completed` and `final=True`.

**`A2AStarletteApplication`** -- The `a2a` SDK's built-in application builder. It takes the agent card and handler, then `build()` produces a Starlette ASGI app with all A2A endpoints pre-wired (agent card discovery, message handling, etc.).

### Entry Point

The `if __name__` block configures logging and runs the built Starlette app through Uvicorn.

## Key Concepts

- **A2A SDK (`a2a` package)**: Unlike the manual JSON-RPC implementations in the LangChain/LangGraph examples, this server uses the official `a2a` Python SDK. The SDK handles protocol compliance, request routing, and response formatting automatically.
- **Stream Handler Pattern**: The `on_message_send_stream` async generator is the primary extension point. Each `yield` emits an SSE event to the client.
- **TaskStatusUpdateEvent**: The A2A event type that communicates task state transitions (`working` -> `completed`) and partial results to the client.
- **AgentScope Integration**: Although this demo does not invoke a full AgentScope `ReActAgent` (to avoid model dependencies), the structure mirrors how you would wrap an AgentScope agent behind an A2A interface.

## Expected Behavior

After starting, the server logs `Starting AgentScope A2A server at 0.0.0.0:8003`. Verify the agent card:

```bash
curl http://127.0.0.1:8003/.well-known/agent.json
```

When a client sends a message, the server responds with a streaming sequence of status updates, ending with a completed task. The response text follows the pattern: "I am the AgentScope A2A test service. I have received your question: <input>. This is a streaming demo response." (in Chinese).
