# Streaming Chat Agent

**Source:** `examples/agents/demo_chat_agent_stream.py`

## Overview

This example demonstrates how to enable LLM streaming output in OxyGent. By setting `"stream": True` in the LLM parameters and enabling terminal message display, you get a real-time token-by-token response experience both in the web UI and the server terminal. This is ideal for conversational applications that benefit from low-latency incremental output.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`

## How to Run

```bash
python -m examples.agents.demo_chat_agent_stream
```

## Code Walkthrough

### Configuration

```python
Config.set_message_is_show_in_terminal(True)
```

Enables printing of streaming messages (SSE events) directly to the terminal. This is useful for debugging and monitoring the agent's output in real time without opening the web UI.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars; `llm_params={"stream": True}` |
| `qa_agent` | `ChatAgent` | `llm_model="default_llm"` (no custom prompt -- uses default behavior) |

The critical parameter is `llm_params={"stream": True}`, which tells the `HttpLLM` to request a streaming response from the LLM API endpoint. Tokens are delivered incrementally via Server-Sent Events (SSE).

### Entry Point

```python
await mas.start_web_service(first_query="hello")
```

Launches the web service with the initial query "hello".

## Key Concepts

- **Streaming (`stream: True`)** -- the LLM returns tokens incrementally rather than waiting for the full response. This is passed through to the web UI via SSE, providing a typewriter-like experience.
- **`set_message_is_show_in_terminal`** -- when `True`, all SSE messages (including streamed tokens) are printed to the server's terminal output for live monitoring.
- **Minimal agent setup** -- the `ChatAgent` here has no custom prompt, no tools, and no hooks, demonstrating the absolute minimal configuration.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The first query "hello" is sent automatically.
3. The agent's response appears token-by-token in the web UI (streaming effect).
4. The same streaming output is also printed to the terminal in real time.
5. Subsequent queries also stream incrementally.
