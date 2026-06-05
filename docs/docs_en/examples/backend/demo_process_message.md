# Processing and Transforming Outgoing Messages

**Source:** `examples/backend/demo_process_message.py`

## Overview

This example demonstrates how to use the `func_process_message` hook to intercept and transform outgoing messages before they reach the frontend. By modifying the message payload in-flight, you can add formatting, inject metadata, filter sensitive content, or apply custom transformations to the SSE stream. This is particularly useful for post-processing streaming LLM responses.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.backend.demo_process_message
```

## Code Walkthrough

### Configuration

```python
Config.set_message_is_show_in_terminal(True)
```

Enables terminal display of all outgoing messages for debugging purposes.

### Hook Functions

```python
def process_message(dict_message: dict, oxy_request: OxyRequest) -> dict:
    if dict_message["data"]["type"] == "stream":
        dict_message["data"]["content"]["delta"] += "-"
    return dict_message
```

The `process_message` function is a MAS-level hook that is called for every outgoing message. It receives:
- `dict_message`: The message dictionary about to be sent.
- `oxy_request`: The current request context.

In this example, it checks if the message type is `"stream"` (a streaming LLM token) and appends a `"-"` character to each token delta. This visually demonstrates the transformation in the UI output.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `llm_params={"stream": True}` -- enables streaming for visible per-token processing |
| `qa_agent` | `ChatAgent` | Basic chat agent |

### Entry Point

```python
async with MAS(oxy_space=oxy_space, func_process_message=process_message) as mas:
    await mas.start_web_service(first_query="hello")
```

The `func_process_message` hook is passed as a parameter to the `MAS` constructor.

## Key Concepts

- **func_process_message**: A MAS-level hook that intercepts every outgoing message before it is sent to the frontend via SSE. It receives the message dictionary and the current `OxyRequest`, and must return the (possibly modified) message dictionary. Supports both sync and async functions.
- **Stream message structure**: Streaming LLM messages have `type: "stream"` with a `content.delta` field containing the incremental text token.
- **Message transformation**: You can modify any field in the message dictionary -- content, metadata, type -- or even suppress messages by returning `None` or an empty dict.

> All `func_*` hooks in OxyGent support both sync and async functions. Sync functions are automatically wrapped as async at initialization time.

## Expected Behavior

1. The web service starts with streaming enabled.
2. When the LLM responds to `"hello"`, each streaming token is intercepted by the hook.
3. Each token delta has a `"-"` character appended, so the output appears with dashes between characters (e.g., `H-e-l-l-o-` instead of `Hello`).
4. Non-stream messages (like status messages) pass through unmodified.
5. All messages are also printed to the terminal for verification.
