# OxyGent Client Calling Google A2A SDK Server

**Source:** `examples/a2a/google_sdk_interop/demo_oxygent_client_call_google_sdk_server.py`

## Overview

This example demonstrates OxyGent's `A2AClientAgent` connecting to a non-OxyGent A2A server built with the Google A2A SDK. It validates that OxyGent can act as a client to any A2A-compliant server, not just OxyGent servers. The example also shows how to pass custom HTTP headers for authentication or metadata.

## Prerequisites

- Start the Google A2A SDK server first: `PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_google_sdk_a2a_server.py`
- No LLM credentials are needed for the client or the Google SDK server (the server returns echo responses).

## How to Run

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_oxygent_client_call_google_sdk_server.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL = "http://127.0.0.1:8011"` -- the Google A2A SDK server endpoint.
- `CLIENT_NAME = "google_sdk_server_client"` -- the agent's name within the MAS.
- `DEMO_HEADERS` -- custom HTTP headers sent with every request:
  - `x-demo-client: "oxygent-a2a"` -- identifies the client framework.
  - `x-demo-token` -- reads from `GOOGLE_A2A_DEMO_TOKEN` environment variable, defaulting to `"demo-token"`.

### Components (`oxy_space`)

A single component:

- **`A2AClientAgent.minimal()`** with:
  - `name=CLIENT_NAME` -- agent identifier.
  - `server_url=SERVER_URL` -- the Google SDK server endpoint.
  - `streaming=False` -- synchronous message send.
  - `timeout=60` -- request timeout.
  - `enable_task_polling=False` -- no automatic polling.
  - `headers=DEMO_HEADERS` -- custom headers attached to all HTTP requests.

### Custom Headers

Headers are passed in two ways:

1. **At agent construction**: `headers=DEMO_HEADERS` in `A2AClientAgent.minimal()` -- these are attached to every outgoing HTTP request.
2. **Per-request via `shared_data`**: `shared_data={"_headers": DEMO_HEADERS}` in the `OxyRequest` -- this allows per-request header overrides.

### Helper Function: `call_once`

Constructs an `OxyRequest` with the query text and custom headers in `shared_data`, then dispatches to the A2A client agent.

### Entry Point

The `main()` coroutine:

1. Creates a MAS with the A2A client agent.
2. Prints the request headers for verification.
3. Sends the query "Please introduce yourself in one short sentence."
4. Prints the response text and session metadata.

## Key Concepts

- **Cross-Framework Client**: OxyGent's `A2AClientAgent` can connect to any A2A-compliant server, not just OxyGent servers. This validates the universality of the A2A protocol.
- **Custom Headers**: The `headers` parameter and `shared_data["_headers"]` provide mechanisms for passing authentication tokens, tracing headers, or other metadata to the server.
- **No LLM Required**: Since the Google SDK server returns echo responses, this client-only example requires no LLM configuration.

## Expected Behavior

When run (with the Google SDK server already started):

1. Prints the request headers dictionary.
2. Sends the query to the Google SDK server.
3. Prints the echo response: `"Google SDK A2A server reply: I received your question: Please introduce yourself in one short sentence."`.
4. Prints the session identifiers (`context_id` and `task_id`).
