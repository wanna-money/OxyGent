# OxyGent Streaming Client Calling Google A2A SDK Server

**Source:** `examples/a2a/google_sdk_interop/demo_oxygent_stream_client_call_google_sdk_server.py`

## Overview

This example demonstrates OxyGent's streaming `A2AClientAgent` connecting to a Google A2A SDK server. It sends a message via the streaming endpoint and receives the response incrementally. This completes the interoperability matrix by testing OxyGent streaming client against a non-OxyGent streaming server.

## Prerequisites

- Start the Google A2A SDK server first: `PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py`
- No LLM credentials are needed (the Google SDK server returns echo responses).

## How to Run

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_oxygent_stream_client_call_google_sdk_server.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL = "http://127.0.0.1:8011"` -- the Google A2A SDK server endpoint.
- `CLIENT_NAME = "google_sdk_stream_client"` -- agent identifier.
- `Config.set_app_name("demo-oxygent-stream-client-call-google-sdk-server")` -- application name for tracing.

### Components (`oxy_space`)

A single component:

- **`A2AClientAgent.minimal()`** with:
  - `name=CLIENT_NAME` -- agent identifier.
  - `server_url=SERVER_URL` -- the Google SDK server.
  - `streaming=True` -- enables SSE streaming via `message/stream`.
  - `timeout=120` -- longer timeout for streaming.
  - `enable_task_polling=False` -- no automatic polling.

### Helper Function: `call_once`

A minimal request builder that creates an `OxyRequest` and dispatches it to the streaming client agent. The streaming is handled internally by `A2AClientAgent`.

### Entry Point

The `main()` coroutine:

1. Creates a MAS with the streaming client agent.
2. Sends the query "Please explain A2A in one short paragraph."
3. Prints the final assembled response prefixed with `[final]`.
4. Prints the session identifiers.

## Key Concepts

- **Streaming Interoperability**: This validates that OxyGent's streaming client correctly processes SSE events from a non-OxyGent server. The Google SDK server emits character-by-character `TaskStatusUpdateEvent` chunks, and OxyGent's client accumulates them into a final response.
- **Minimal Client Configuration**: The `.minimal()` factory creates a fully functional streaming client with just a few parameters -- no LLM, agent card, or complex setup required.
- **Interop Matrix**: Together with the other interop examples, this completes all four combinations: OxyGent client/server, OxyGent client + Google server, Google client + OxyGent server, and Google client/server.

## Expected Behavior

When run (with the Google SDK server already started):

1. The `A2AClientAgent` resolves the agent card from `http://127.0.0.1:8011/.well-known/agent.json`.
2. Sends the query via the streaming endpoint.
3. Receives character-by-character SSE events from the Google SDK server.
4. Prints `[final]` followed by the complete echo response: `"Google SDK stream reply: Please explain A2A in one short paragraph."`.
5. Prints the session identifiers (`context_id` and `task_id`).
