# Controlling Message Storage and Delivery

**Source:** `examples/backend/demo_save_message.py`

## Overview

This example demonstrates fine-grained control over message storage and delivery in OxyGent. It shows how to send custom messages from within agent hooks and control whether each message is persisted to Elasticsearch and/or pushed to the frontend via SSE. This pattern is useful when you need to send progress updates, status notifications, or debugging information while selectively choosing which messages are saved for later retrieval.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`

## How to Run

```bash
python -m examples.backend.demo_save_message
```

## Code Walkthrough

### Configuration

```python
Config.set_message_is_show_in_terminal(True)
Config.set_message_is_stored(True)
```

- `set_message_is_show_in_terminal(True)`: Enables printing messages to the terminal for debugging.
- `set_message_is_stored(True)`: Sets the global default to store messages in Elasticsearch.

### Hook Functions

```python
async def update_query(oxy_request: OxyRequest) -> OxyRequest:
    await oxy_request.send_message(
        {"type": "test1", "content": "test1", "_is_stored": False, "_is_send": False}
    )
    await oxy_request.send_message(
        {"type": "test2", "content": "test2", "_is_stored": False, "_is_send": True}
    )
    await oxy_request.send_message(
        {"type": "test3", "content": "test3", "_is_stored": True, "_is_send": False}
    )
    await oxy_request.send_message(
        {"type": "test4", "content": "test4", "_is_stored": True, "_is_send": True}
    )
    return oxy_request
```

Four messages are sent with different combinations of `_is_stored` and `_is_send` flags:

| Message | `_is_stored` | `_is_send` | Behavior |
|---------|-------------|-----------|----------|
| test1 | `False` | `False` | Neither stored nor sent to frontend |
| test2 | `False` | `True` | Sent to frontend via SSE but not persisted |
| test3 | `True` | `False` | Persisted to ES but not sent to frontend |
| test4 | `True` | `True` | Both persisted and sent to frontend |

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `llm_params={"stream": True}` -- enables streaming responses |
| `qa_agent` | `ChatAgent` | `func_process_input=update_query` -- sends custom messages before processing |

### Entry Point

```python
async with MAS(oxy_space=oxy_space) as mas:
    await mas.start_web_service(first_query="hello")
```

## Key Concepts

- **send_message**: An async method on `OxyRequest` that pushes custom messages into the MAS message pipeline. Each message is a dictionary with a `type` and `content`.
- **_is_stored flag**: Controls whether the message is persisted to Elasticsearch. Useful for audit trails and conversation history.
- **_is_send flag**: Controls whether the message is pushed to the frontend via SSE/Redis. Useful for real-time UI updates.
- **Streaming LLM**: Setting `llm_params={"stream": True}` enables token-by-token streaming from the LLM, which works alongside the custom message pipeline.

## Expected Behavior

1. When the agent processes a query, four custom messages are emitted.
2. `test1` is silently discarded (neither stored nor sent).
3. `test2` appears in the frontend SSE stream but is not saved to Elasticsearch.
4. `test3` is saved to Elasticsearch but does not appear in the frontend.
5. `test4` both appears in the frontend and is saved to Elasticsearch.
6. All four messages are printed to the terminal (because `is_show_in_terminal` is enabled).
7. The LLM response streams to the frontend after the custom messages.
