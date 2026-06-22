# AgentScope Client Calling OxyGent A2A Server

**Source:** `examples/a2a/agentscope_interop/demo_agentscope_client_call_oxygent_server.py`

## Overview

This example uses AgentScope's built-in `A2AAgent` class to call an OxyGent A2A server. It demonstrates how an AgentScope agent can interoperate with OxyGent by constructing an `AgentCard` pointing to the OxyGent server and sending messages through AgentScope's native `Msg` interface. This is the simplest possible AgentScope-as-client example.

## Prerequisites

- Python 3.10+
- Extra packages: `pip install agentscope a2a`
- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME` (required by the OxyGent server)
- **The OxyGent A2A server must be running first:**
  ```bash
  PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
  ```

## How to Run

```bash
PYTHONPATH=. python examples/a2a/agentscope_interop/demo_agentscope_client_call_oxygent_server.py
```

## Code Walkthrough

### Configuration

The client targets `http://127.0.0.1:8090/a2a`, the default OxyGent A2A server. The `AgentCard` is constructed with `streaming=False` to use the non-streaming `message/send` path, avoiding async stream-close race conditions in the AgentScope demo runtime.

### Components

**`build_oxygent_agent_card()`** -- Creates an `AgentCard` using the official `a2a.types` models. This card describes the remote OxyGent server's endpoint, capabilities, and skills. The card is passed to `A2AAgent` so it knows where and how to communicate.

**`A2AAgent`** -- AgentScope's built-in agent class for A2A interoperability. Initialized with the agent card, it automatically handles:
- Agent card-based endpoint discovery
- A2A message formatting and sending
- Response parsing

**`Msg`** -- AgentScope's standard message type. The client creates a `Msg` with `role="user"` and the query content, then passes it to the `A2AAgent` via the `await agent(msg)` call pattern.

### Entry Point

The `main()` coroutine:
1. Instantiates an `A2AAgent` with the OxyGent agent card.
2. Creates a user message asking "which number is largest: 1, 5, 7" (in Chinese).
3. Sends the message and awaits the response.
4. Prints the response text content.
5. Includes a brief `asyncio.sleep(0.1)` for clean shutdown.

## Key Concepts

- **AgentScope A2AAgent**: A native AgentScope component that wraps A2A protocol communication. It accepts an `AgentCard` and exposes a callable interface compatible with AgentScope's message-passing patterns.
- **AgentCard as Connection Descriptor**: The `AgentCard` serves as a complete description of the remote agent -- its URL, capabilities, and skills. By constructing one manually, any A2A server becomes accessible.
- **Non-Streaming for Simplicity**: The example deliberately sets `streaming=False` to avoid async complexity in the demo runtime. Production deployments can enable streaming.
- **Cross-Framework Interop**: AgentScope natively consumes an OxyGent-hosted agent through the A2A protocol, requiring only the agent card as configuration.

## Expected Behavior

The client sends a math question to the OxyGent server. Console output shows:
- `[turn1]` -- the LLM-generated answer from the OxyGent server (the actual answer depends on the configured LLM).

The interaction is a single turn with no multi-turn session management.
