# A2A OxyGent Task Follow-Up Client

**Source:** `examples/a2a/demo_a2a_oxygent_task_followup_client.py`

## Overview

This example demonstrates multi-turn A2A conversations using `context_id` and `reference_task_ids`. It sends two sequential messages to the A2A server: the first asks a question, and the second references the first task to ask a follow-up question, validating that the server maintains conversational context across A2A tasks.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME` (required by the server)
- Start the A2A server first: `PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_server.py`

## How to Run

```bash
PYTHONPATH=. python examples/a2a/demo_a2a_oxygent_task_followup_client.py
```

## Code Walkthrough

### Configuration

- `SERVER_URL = "http://127.0.0.1:8090/a2a"` -- the A2A server endpoint.
- `Config.set_app_name("demo-a2a-oxygent-task-followup-client")` -- application name for tracing.

### Components (`oxy_space`)

A single component:

- **`A2AClientAgent.minimal()`** with:
  - `name="a2a_client"` -- agent identifier.
  - `streaming=False` -- synchronous message send.
  - `timeout=60` -- request timeout.
  - `enable_task_polling=True` -- enables automatic task status polling, which is important for follow-up scenarios where the server may need time to process context.

### Helper Function: `call_once`

Similar to the basic client example, but with full support for multi-turn parameters:

- `context_id` -- links messages within the same conversation session.
- `task_id` -- references a specific prior task for continuation.
- `reference_task_ids` -- a list of task IDs whose context should be considered by the server when processing the new message.

### Entry Point

The `main()` coroutine executes a two-turn conversation:

**Turn 1:**
1. Sends the query "Which number is the largest? Give the result directly: 1, 5, 7" (in Chinese).
2. Extracts `context_id` and `task_id` from the response.
3. Validates that both session identifiers are present; raises `RuntimeError` if missing.

**Turn 2 (after a 1-second pause):**
1. Sends the follow-up "Which number is the smallest?" using the `context_id` from turn 1.
2. Passes `reference_task_ids=[task_id]` so the server knows this message relates to the previous task.
3. Prints the response, which should correctly identify "1" as the smallest number from the original set, demonstrating context retention.

## Key Concepts

- **`context_id`**: A session identifier that groups multiple A2A tasks into a single conversation. The server uses this to maintain conversation history.
- **`reference_task_ids`**: Explicitly links a new task to one or more prior tasks. The server can use these references to load relevant context from previous interactions.
- **`enable_task_polling=True`**: When enabled, the client agent will automatically poll the server for task completion if the initial response indicates the task is still in progress.
- **Multi-Turn Context**: The A2A protocol supports stateful conversations. By passing `context_id` and `reference_task_ids`, agents can maintain coherent multi-turn dialogues.

## Expected Behavior

When run (with the server already started):

1. **Turn 1**: Prints `[turn1]` followed by the answer "7" (the largest number), along with session identifiers.
2. **Turn 2**: Prints `[turn2]` followed by the answer "1" (the smallest number), demonstrating that the server correctly understood the follow-up question in the context of the first turn's number set.
3. Both turns share the same `context_id`, while each has its own `task_id`.
