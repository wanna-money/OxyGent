# Google A2A SDK Streaming Client Calling OxyGent Server

**Source:** `examples/a2a/google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.py`

## Overview

This example uses the Google A2A SDK to call an OxyGent A2A server in streaming mode. It sends a message via the `message/stream` endpoint and processes SSE chunks in real time, printing incremental text deltas as they arrive. The example includes helper logic to extract text from various A2A event types (`Message`, `Task`, `TaskStatusUpdateEvent`, `TaskArtifactUpdateEvent`).

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME` (required by the server)
- Extra packages: `pip install a2a-sdk`
- Start the OxyGent A2A server first: `PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## How to Run

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_a2a_sdk_stream_call_oxygent.py
```

## Code Walkthrough

### Configuration

- `base_url = "http://127.0.0.1:8090/a2a"` -- the OxyGent A2A server endpoint.
- `card_path = ".well-known/agent.json"` -- agent card discovery path.
- HTTP timeout is set to 120 seconds to accommodate streaming.

### Helper Function: `extract_text`

A utility function that extracts text content from the various result types that can appear in A2A streaming chunks:

- **`Message`**: Uses `get_message_text()` from the A2A SDK utilities.
- **`Task`**: Extracts text from both the task's status message and any artifacts.
- **`TaskStatusUpdateEvent`**: Extracts text from the event's status message.
- **`TaskArtifactUpdateEvent`**: Extracts text from the artifact's parts.

This function handles the polymorphic nature of A2A streaming responses, where different chunk types carry text in different structures.

### Streaming Message Send

The message payload is constructed identically to the non-streaming example, then wrapped in a `SendStreamingMessageRequest`:

```python
req = SendStreamingMessageRequest(
    id=str(uuid4()),
    params=MessageSendParams(**payload),
)
```

The response is consumed via an async iterator:

```python
async for chunk in client.send_message_streaming(req):
    ...
```

### Delta Computation

The streaming loop maintains an `emitted` string tracking all text printed so far. For each chunk:

1. Extracts the text content via `extract_text`.
2. Computes the delta (new characters not yet printed).
3. Prints the delta immediately with `end=''` for a typewriter effect.
4. Updates the `emitted` accumulator.

This approach handles servers that send cumulative text (where each chunk contains the full text so far) as well as servers that send only incremental deltas.

### Entry Point

The `main()` coroutine:

1. Resolves the agent card and prints the server URL.
2. Creates an `A2AClient`.
3. Sends a streaming request asking the server to describe OxyGent A2A streaming capabilities in three points.
4. Prints chunks in real time as they arrive.
5. Prints the final accumulated text after the stream ends.

## Key Concepts

- **SSE Streaming**: The A2A protocol supports Server-Sent Events for real-time response delivery. Each SSE event carries a JSON-RPC response containing a `TaskStatusUpdateEvent` or `TaskArtifactUpdateEvent`.
- **Polymorphic Chunk Types**: A2A streaming responses can contain `Message`, `Task`, `TaskStatusUpdateEvent`, or `TaskArtifactUpdateEvent` objects. Robust clients must handle all types.
- **Delta Accumulation**: Since different A2A servers may send either cumulative or incremental text, the delta logic ensures correct display regardless of server behavior.
- **Cross-Framework Streaming**: This validates that OxyGent's streaming A2A endpoint is compatible with the Google A2A SDK's streaming client.

## Expected Behavior

When run (with the OxyGent server already started):

1. Prints `[card]` followed by the server URL.
2. Prints `[stream begin]`, then streams the response text character by character (or chunk by chunk).
3. Prints `[stream end]` when the SSE stream closes.
4. Prints `[final]` followed by the complete accumulated response text.
