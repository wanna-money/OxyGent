# LangGraph Client Calling OxyGent A2A Server

**Source:** `examples/a2a/langgraph_interop/demo_langgraph_client_call_oxygent_server.py`

## Overview

This example builds a LangGraph `StateGraph` that acts as a client to an OxyGent A2A server. The graph contains a single node that makes an A2A `message/send` call via HTTP, demonstrating how LangGraph's stateful graph execution can incorporate external A2A agents as graph nodes.

## Prerequisites

- Python 3.10+
- Extra packages: `pip install langgraph httpx`
- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME` (required by the OxyGent server)
- **The OxyGent A2A server must be running first:**
  ```bash
  PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py
  ```

## How to Run

```bash
PYTHONPATH=. python examples/a2a/langgraph_interop/demo_langgraph_client_call_oxygent_server.py
```

## Code Walkthrough

### Configuration

The client connects to `http://127.0.0.1:8090/a2a`, the default OxyGent A2A server endpoint.

### Components

**`GraphState`** -- A `TypedDict` with five fields: `query`, `answer`, `context_id`, `task_id`, and `raw_task`. This state flows through the graph and captures both the A2A response and session metadata.

**`extract_task_text(task)`** -- Extracts the text answer from an A2A task, checking `status.message.parts` first and falling back to `artifacts[0].parts`.

**`send_a2a(query, context_id, task_id)`** -- An async function that constructs an A2A `message/send` JSON-RPC payload and sends it via httpx. Returns the raw task dict and extracted text. Supports optional `contextId` and `taskId` for multi-turn sessions.

**`call_node(state)`** -- The graph node function. It calls `send_a2a` with the current query and session state, then returns the updated `GraphState` with the answer and session identifiers populated from the A2A response.

**Compiled Graph** -- A `StateGraph` with a single `call` node connected to `END`. The graph is compiled into an executable that can be invoked with `ainvoke`.

### Entry Point

The `main()` coroutine:
1. Invokes the graph with an initial query asking "which number is largest: 1, 5, 7" (in Chinese).
2. Prints the raw task JSON and the extracted answer.

## Key Concepts

- **A2A as a Graph Node**: By wrapping the A2A HTTP call inside a LangGraph node, external agents become first-class participants in graph-based workflows. More nodes could be added for pre/post-processing or multi-agent orchestration.
- **Stateful Session Tracking**: The `GraphState` carries `context_id` and `task_id` across graph invocations, enabling multi-turn conversations through the A2A protocol.
- **Async Graph Execution**: The `ainvoke` method runs the graph asynchronously, which is necessary because the A2A call itself is async.
- **Cross-Framework Interop**: A LangGraph workflow consumes an OxyGent-powered agent through the framework-agnostic A2A protocol.

## Expected Behavior

The client sends a math question to the OxyGent server via the LangGraph pipeline. Console output includes:
- `[turn1 raw]` -- the full A2A task JSON returned by the OxyGent server
- `[turn1]` -- the extracted LLM answer text
