# Google A2A SDK Client Calling OxyGent Server

**Source:** `examples/a2a/google_sdk_interop/demo_a2a_sdk_call_oxygent.py`

## Overview

This example uses the official Google A2A SDK (`a2a-sdk`) client to call an OxyGent A2A server. It demonstrates cross-framework interoperability: the client is built entirely with the Google A2A SDK types and client classes, while the server is a standard OxyGent MAS with A2A enabled. The example resolves the agent card, sends a non-streaming message, and optionally polls for task completion.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME` (required by the server)
- Extra packages: `pip install a2a-sdk`
- Start the OxyGent A2A server first: `PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## How to Run

```bash
PYTHONPATH=. python examples/a2a/google_sdk_interop/demo_a2a_sdk_call_oxygent.py
```

## Code Walkthrough

### Configuration

- `base_url = "http://127.0.0.1:8090/a2a"` -- the OxyGent A2A server endpoint.
- `agent_card_path = ".well-known/agent.json"` -- standard A2A agent card discovery path.
- `streaming = False` -- uses synchronous `message/send`.
- `enable_polling = True` -- enables task polling after the initial response.

### Agent Card Resolution

The example uses `A2ACardResolver` from the Google SDK to discover the agent card:

```python
resolver = A2ACardResolver(
    httpx_client=httpx_client,
    base_url=base_url,
    agent_card_path=agent_card_path,
)
card: AgentCard = await resolver.get_agent_card()
```

The resolved `AgentCard` contains the agent's name, capabilities, skills, and URL, which the `A2AClient` uses to validate and route requests.

### Sending a Message

The message payload follows the A2A protocol structure:

- `message.role` -- set to `"user"`.
- `message.parts` -- a list containing a `TextPart` with the query text.
- `message.messageId` -- a unique identifier generated via `uuid4().hex`.

The payload is wrapped in a `SendMessageRequest` (or `SendStreamingMessageRequest` if `streaming=True`) and sent via `client.send_message()`.

### Task Polling: `poll_task`

The `poll_task` function repeatedly calls `client.get_task()` until the task reaches a terminal state (`completed`, `failed`, `canceled`, `rejected`) or the polling timeout is exceeded. It:

1. Constructs a `GetTaskRequest` with the target `task_id`.
2. Inspects the response for the task's `status.state`.
3. Sleeps for `interval_seconds` between polls.
4. Times out after `max_wait_seconds`.

### Entry Point

The `main()` coroutine:

1. Creates an `httpx.AsyncClient` with a 60-second timeout.
2. Resolves the agent card and prints it.
3. Creates an `A2AClient` bound to the resolved card.
4. Sends a query ("Calculate the result of 1+1" in Chinese).
5. Prints the full JSON response from the server.

## Key Concepts

- **Cross-Framework Interoperability**: This example proves that OxyGent's A2A server implementation is fully compatible with the Google A2A SDK client, validating protocol compliance.
- **`A2ACardResolver`**: The Google SDK's mechanism for discovering agent capabilities via the `.well-known/agent.json` endpoint.
- **`A2AClient`**: The Google SDK's HTTP client for sending messages and managing tasks against an A2A-compliant server.
- **Task Polling**: A pattern for handling asynchronous task completion when the server does not return results immediately.

## Expected Behavior

When run (with the OxyGent server already started):

1. Prints the agent card JSON showing the server's capabilities and skills.
2. Sends the math query and prints the full JSON-RPC response, which includes the task ID, status, and the agent's answer.
3. If polling is enabled and the task is not immediately complete, polls until the task reaches a terminal state.
