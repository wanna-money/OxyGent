# Single Chat Agent with Custom Hooks

**Source:** `examples/agents/demo_single_agent.py`

## Overview

This example demonstrates the simplest OxyGent setup: a single `ChatAgent` backed by one `HttpLLM`, enhanced with custom input-processing and output-formatting hook functions. It is the ideal starting point for understanding the Oxy lifecycle and how to inject custom logic before and after agent execution.

## Prerequisites

- Environment variables: `DEFAULT_LLM_API_KEY`, `DEFAULT_LLM_BASE_URL`, `DEFAULT_LLM_MODEL_NAME`
- Python packages listed in `requirements.txt`

## How to Run

```bash
python -m examples.agents.demo_single_agent
```

## Code Walkthrough

### Configuration

```python
Config.set_agent_short_memory_size(7)
```

Sets the conversation short-memory window to 7 turns. This controls how many recent user/assistant message pairs the agent retains as context when calling the LLM.

### Hook Functions

#### `update_query(oxy_request: OxyRequest) -> OxyRequest`

A **pre-processing** hook registered via `func_process_input`. It appends `" Please answer in detail."` to every incoming user query before the agent processes it. This demonstrates how to transparently modify user input.

#### `format_output(oxy_response: OxyResponse) -> OxyResponse`

A **post-processing** hook registered via `func_format_output`. It prepends `"Answer: "` to the agent's output string. This demonstrates how to uniformly format all responses before they reach the user.

### Components (`oxy_space`)

| Component | Type | Key Parameters |
|-----------|------|----------------|
| `default_llm` | `HttpLLM` | `api_key`, `base_url`, `model_name` from env vars; `llm_params={"temperature": 0.01}`; `semaphore=4` (max 4 concurrent requests); `timeout=300` (5-minute timeout); `retries=3` |
| `master_agent` | `ChatAgent` | `llm_model="default_llm"`; `prompt="You are a helpful assistant."`; `func_process_input=update_query`; `func_format_output=format_output` |

### Entry Point

`main()` creates a `MAS` instance with the `oxy_space` list and launches the web service:

```python
await mas.start_web_service(
    first_query="Hello",
    welcome_message="Hi, I'm OxyGent. How can I assist you?",
)
```

- `first_query="Hello"` -- sends an initial query automatically when the web UI loads.
- `welcome_message` -- the greeting displayed in the web UI before any interaction.

## Key Concepts

- **`func_process_input`** -- a callback invoked in the `_format_input` phase of the Oxy lifecycle, allowing mutation of the `OxyRequest` before execution.
- **`func_format_output`** -- a callback invoked in the `_format_output` phase, allowing mutation of the `OxyResponse` after execution.
- **`semaphore`** -- limits concurrent LLM API calls to prevent rate-limiting or resource exhaustion.
- **`short_memory_size`** -- controls the sliding window of conversation history sent to the LLM.

## Expected Behavior

1. The web service starts at `http://127.0.0.1:8080`.
2. The welcome message "Hi, I'm OxyGent. How can I assist you?" appears in the chat UI.
3. The first query "Hello" is automatically sent, but internally the agent processes "Hello Please answer in detail." due to the `update_query` hook.
4. The agent's response is prefixed with "Answer: " due to the `format_output` hook.
5. Subsequent user messages are also processed through both hooks.
