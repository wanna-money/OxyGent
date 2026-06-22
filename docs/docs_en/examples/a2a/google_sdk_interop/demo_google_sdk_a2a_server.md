# Google A2A SDK Server

**Source:** `examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py`

## Overview

This example implements a minimal A2A server using the official Google A2A SDK (`a2a-sdk`). It does not use OxyGent at all -- instead, it serves as a standalone A2A-compliant server that OxyGent clients can connect to, validating cross-framework interoperability from the other direction. The server supports both synchronous and streaming message handling with simple echo-style responses.

## Prerequisites

- Extra packages: `pip install a2a-sdk uvicorn`
- No LLM credentials required -- this server returns hardcoded echo responses.

## How to Run

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py
```

The server starts on `http://127.0.0.1:8011`.

## Code Walkthrough

### Configuration

- `HOST = "0.0.0.0"` -- binds to all interfaces.
- `PORT = 8011` -- the HTTP port.
- `BASE_URL = f"http://127.0.0.1:{PORT}"` -- the advertised URL in the agent card.

### Agent Card: `build_agent_card`

Constructs an `AgentCard` describing the server's capabilities:

- **`name`**: `"google_sdk_demo_server"` -- the agent's display name.
- **`capabilities`**: `push_notifications=False`, `state_transition_history=True`, `streaming=True`.
- **`default_input_modes` / `default_output_modes`**: Both set to `["text/plain"]`.
- **`skills`**: A single skill named `"chat"` with tags `["a2a", "sdk", "interop"]`.

### Handler: `SimpleA2AHandler`

The handler class implements two methods that the A2A SDK framework dispatches to:

#### `on_message_send`

Handles synchronous `message/send` requests:

1. Extracts the query text from `params.message` via `get_message_text`.
2. Preserves `context_id` and `task_id` from the incoming message.
3. Returns a `Message` with an echo-style reply: `"Google SDK A2A server reply: I received your question: {query}"`.

#### `on_message_send_stream`

Handles streaming `message/stream` requests:

1. Yields an initial `TaskStatusUpdateEvent` with `state=TaskState.working`.
2. Iterates character by character through the response text, yielding a `TaskStatusUpdateEvent` for each character with cumulative text. Each event includes a 0.1-second delay to simulate real-time generation.
3. Yields a final `TaskStatusUpdateEvent` with `state=TaskState.completed`.

### Application Setup

The `A2AStarletteApplication` from the Google SDK wires the agent card and handler into a Starlette ASGI application:

```python
app = A2AStarletteApplication(
    agent_card=build_agent_card(),
    http_handler=handler,
).build()
```

This is served via `uvicorn.run()`.

## Key Concepts

- **Google A2A SDK Server**: The `a2a-sdk` package provides `A2AStarletteApplication` for building A2A-compliant servers without OxyGent. This is the "other side" of the interop story.
- **Handler Pattern**: The SDK uses a handler class with `on_message_send` and `on_message_send_stream` methods. The framework dispatches incoming JSON-RPC requests to the appropriate handler.
- **Streaming via AsyncGenerator**: Streaming responses are implemented as Python async generators that yield `Event` objects (specifically `TaskStatusUpdateEvent`). The SDK converts these to SSE events.
- **Character-by-Character Streaming**: The streaming handler simulates token-level streaming by emitting one character at a time with a 100ms delay.

## Expected Behavior

When started:

1. Logs `"Starting Google SDK A2A demo server at 0.0.0.0:8011"`.
2. Serves the agent card at `http://127.0.0.1:8011/.well-known/agent.json`.
3. For non-streaming requests: returns an echo response immediately.
4. For streaming requests: emits character-by-character SSE events, then a final `completed` event.
5. Remains running until manually terminated (Ctrl+C).
