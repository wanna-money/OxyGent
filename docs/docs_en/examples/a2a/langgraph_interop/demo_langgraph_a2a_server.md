# LangGraph A2A Server

**Source:** `examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py`

## Overview

This example launches a minimal A2A-compliant server powered by LangGraph. It exposes a FastAPI application on port 8102 that implements the core A2A JSON-RPC methods (`message/send`, `message/stream`, `tasks/get`, `tasks/cancel`) and serves an Agent Card at the `.well-known/agent.json` discovery endpoint. The underlying logic is a compiled LangGraph `StateGraph` with a single node that echoes input with a `[LangGraph Server]` prefix.

## Prerequisites

- Python 3.10+
- Extra packages: `pip install langgraph fastapi uvicorn sse-starlette`
- No LLM API keys are required -- the server uses a deterministic echo graph.

## How to Run

```bash
PYTHONPATH=. python examples/a2a/langgraph_interop/demo_langgraph_a2a_server.py
```

The server starts at `http://127.0.0.1:8102/a2a`.

## Code Walkthrough

### Configuration

| Constant | Value | Purpose |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | Listen address |
| `APP_PORT` | `8102` | Listen port |
| `BASE_PATH` | `/a2a` | Root path for all A2A endpoints |

An in-memory `TASKS` dictionary stores completed tasks for retrieval via `tasks/get`.

### Components

**`GraphState`** -- A `TypedDict` defining the LangGraph state schema with `query` and `answer` fields.

**`answer_node(state)`** -- The single graph node. It takes the input query and returns the state with the answer set to `[LangGraph Server] <query>`.

**Compiled Graph** -- A `StateGraph` with one node (`answer`) connected directly to `END`. The `builder.compile()` call produces the executable graph. This minimal graph can be extended with additional nodes, conditional edges, and loops for more complex agent behavior.

**Helper functions** -- `extract_text`, `build_message`, and `build_task` serve the same roles as in the LangChain server example: parsing A2A message payloads and constructing A2A-compliant response objects.

**A2A endpoints:**

| Method | Behavior |
|---|---|
| `message/send` | Invokes the graph synchronously and returns the completed task. |
| `message/stream` | Invokes the graph, then emits the answer character-by-character as SSE events. |
| `tasks/get` | Retrieves a previously completed task by ID. |
| `tasks/cancel` | Marks a task as `canceled`. |

**Agent Card** (`GET /a2a/.well-known/agent.json`) -- Returns metadata with framework tag `langgraph`, capabilities (streaming, task control), and a single `chat` skill.

### Entry Point

The `main()` coroutine creates a Uvicorn server config and serves the FastAPI app. Running the script calls `asyncio.run(main())`.

## Key Concepts

- **LangGraph StateGraph**: A directed graph where nodes transform a shared typed state. This example uses the simplest possible graph (one node to END), but the pattern scales to multi-step reasoning with cycles and conditionals.
- **A2A Protocol Compliance**: The server follows the A2A JSON-RPC 2.0 specification, making it callable by any A2A client regardless of framework.
- **Streaming via SSE**: The `message/stream` method simulates token-by-token streaming using Server-Sent Events.
- **Agent Card**: The `.well-known/agent.json` endpoint allows automatic discovery by A2A clients.

## Expected Behavior

After starting, Uvicorn logs confirm the server is listening on `127.0.0.1:8102`. Verify the agent card with:

```bash
curl http://127.0.0.1:8102/a2a/.well-known/agent.json
```

A `message/send` request returns a completed task with an answer like `[LangGraph Server] <your input>`. The server is designed to be called by the OxyGent client and OxyGent streaming client examples in this directory.
