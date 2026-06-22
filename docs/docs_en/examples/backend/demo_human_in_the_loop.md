# Human-in-the-Loop with Feedback Streams

**Source:** `examples/backend/demo_human_in_the_loop.py`

## Overview

This example demonstrates the human-in-the-loop pattern in OxyGent, where an agent pauses execution to wait for external feedback before continuing. Using `send_message` to notify the frontend and `get_feedback_stream` to listen for responses, this pattern enables interactive workflows that require human approval, input, or intervention during agent execution.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.backend.demo_human_in_the_loop
```

## Code Walkthrough

### Hook Functions

```python
async def workflow(oxy_request: OxyRequest):
    # Send a message to the frontend
    await oxy_request.send_message({"type": "msg_type", "content": "msg_content"})

    # Listen for feedback; channel_id defaults to trace_id
    feedbacks = []
    async for data in oxy_request.get_feedback_stream():
        print(data)
        feedbacks.append(data)

    return ",".join(feedbacks)
```

The workflow function:
1. Sends a custom message to the frontend (e.g., prompting the user for input).
2. Opens a feedback stream using `get_feedback_stream()`, which blocks and yields data as it arrives.
3. Collects all feedback items and returns them as a comma-separated string.

External clients can send feedback via the `/feedback` endpoint:
```
POST http://127.0.0.1:8080/feedback
Body: {"channel_id": "xxx", "data": "user input here"}
```

The `channel_id` defaults to the current `trace_id`.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | Standard LLM credentials (included but not used directly in the workflow) |
| `master_agent` | `WorkflowAgent` | `func_workflow=workflow` -- custom async workflow with human interaction |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## Key Concepts

- **Human-in-the-loop**: A design pattern where automated agent execution pauses to request and incorporate human input before proceeding.
- **send_message**: Pushes a message to the frontend via the SSE stream, used here to prompt the user for feedback.
- **get_feedback_stream**: An async generator on `OxyRequest` that yields feedback data as it arrives from external sources. The stream is keyed by `channel_id` (defaulting to `trace_id`).
- **Feedback endpoint**: The MAS web service exposes `POST /feedback` where external systems or the frontend can send data back to a waiting agent.
- **WorkflowAgent**: Executes a user-defined async function instead of LLM-driven reasoning, giving full control over the execution flow including pauses for human input.

## Expected Behavior

1. The web service starts and the workflow agent processes the initial query `"hello"`.
2. The agent sends a message `{"type": "msg_type", "content": "msg_content"}` to the frontend.
3. The agent then blocks, waiting for feedback via `get_feedback_stream()`.
4. When a user or external system sends a POST request to `/feedback` with the appropriate `channel_id`, the data is yielded by the stream.
5. The agent collects all feedback, joins it with commas, and returns it as the final response.
