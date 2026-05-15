# LangChain A2A Server

**Source:** `examples/a2a/langchain_interop/demo_langchain_a2a_server.py`

## Overview

This example launches a minimal A2A-compliant server powered by LangChain. It exposes a FastAPI application on port 8101 that implements the core A2A JSON-RPC methods (`message/send`, `message/stream`, `tasks/get`, `tasks/cancel`) and serves an Agent Card at the `.well-known/agent.json` discovery endpoint. The underlying logic is a simple `RunnableLambda` chain that echoes input with a `[LangChain Server]` prefix.

## Prerequisites

- Python 3.10+
- Extra packages: `pip install langchain-core fastapi uvicorn sse-starlette`
- No LLM API keys are required -- the server uses a deterministic echo chain.

## How to Run

```bash
PYTHONPATH=. python examples/a2a/langchain_interop/demo_langchain_a2a_server.py
```

The server starts at `http://127.0.0.1:8101/a2a`.

## Code Walkthrough

### Configuration

| Constant | Value | Purpose |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | Listen address |
| `APP_PORT` | `8101` | Listen port |
| `BASE_PATH` | `/a2a` | Root path for all A2A endpoints |

An in-memory `TASKS` dictionary stores completed tasks so they can be retrieved later via `tasks/get`.

### Components

**`chain`** -- A LangChain `RunnableLambda` that prepends `[LangChain Server]` to any input string. This represents the agent logic and can be replaced with any LangChain chain or agent.

**`extract_text(payload)`** -- Parses an A2A `params` dict to pull the user's text from the nested `message.parts` structure, falling back to top-level `query` or `text` fields.

**`build_message(text, task_id, context_id)`** -- Constructs an A2A `message` event with role `agent`.

**`build_task(text, task_id, context_id)`** -- Wraps a message into a full A2A `task` object with `completed` state and an artifact containing the answer.

**A2A endpoints:**

| Method | Behavior |
|---|---|
| `message/send` | Invokes the chain synchronously and returns the completed task. |
| `message/stream` | Invokes the chain, then emits the answer character-by-character as SSE events (simulating streaming). |
| `tasks/get` | Retrieves a previously completed task by ID. |
| `tasks/cancel` | Marks a task as `canceled`. |

**Agent Card** (`GET /a2a/.well-known/agent.json`) -- Returns metadata describing the server's name, capabilities (streaming, task control), and a single `chat` skill.

### Entry Point

The `main()` coroutine creates a Uvicorn server config and serves the FastAPI app. Running the script directly calls `asyncio.run(main())`.

## Key Concepts

- **A2A Protocol**: The server implements Google's Agent-to-Agent protocol over JSON-RPC 2.0, enabling cross-framework agent interoperability.
- **Agent Card Discovery**: Clients discover the server's capabilities by fetching `/.well-known/agent.json`.
- **RunnableLambda**: The simplest LangChain primitive -- wraps a plain Python function into a runnable. Swap it for a real LangChain chain to build production agents.
- **Streaming via SSE**: The `message/stream` method returns an `EventSourceResponse`, sending partial results as Server-Sent Events.

## Expected Behavior

After starting the server, you should see Uvicorn log output confirming it is listening on `127.0.0.1:8101`. You can verify the agent card with:

```bash
curl http://127.0.0.1:8101/a2a/.well-known/agent.json
```

Sending a `message/send` request will return a JSON-RPC response containing the completed task with an answer like `[LangChain Server] <your input>`. The server is designed to be called by the OxyGent client or OxyGent streaming client examples in this directory.
