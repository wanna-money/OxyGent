# Disable System Prompt Demo

**Source:** `examples/llms/demo_disable_system_prompt.py`

## Overview

This example shows how to disable the system prompt when using an LLM that does not support the `system` role in its message format. Some models (particularly certain proprietary or fine-tuned models) reject or ignore system prompts. The `is_disable_system_prompt` flag on `HttpLLM` strips the system message before sending requests to such models.

## Prerequisites

- Environment variables (set in `.env` or shell):
  - `CHATRHINO_750B_API_KEY` -- API key for the ChatRhino 750B model
  - `CHATRHINO_750B_BASE_URL` -- Base URL of the ChatRhino API
  - `CHATRHINO_750B_MODEL_NAME` -- Model name for ChatRhino 750B
- Python 3.10+ with project dependencies installed

**Note:** This example uses model-specific environment variables (`CHATRHINO_750B_*`) rather than the default `DEFAULT_LLM_*` variables, since it targets a specific model that lacks system prompt support.

## How to Run

```bash
python -m examples.llms.demo_disable_system_prompt
```

## Code Walkthrough

### Configuration

```python
oxy.HttpLLM(
    name="default_llm",
    api_key=os.getenv("CHATRHINO_750B_API_KEY"),
    base_url=os.getenv("CHATRHINO_750B_BASE_URL"),
    model_name=os.getenv("CHATRHINO_750B_MODEL_NAME"),
    is_disable_system_prompt=True,
)
```

The key parameter is `is_disable_system_prompt=True`. When enabled, the framework automatically removes any system-role message from the conversation before sending it to the LLM API. This ensures compatibility with models that do not support the system prompt role.

### Components (`oxy_space`)

1. **`HttpLLM("default_llm")`** -- An HTTP-based LLM with system prompt disabled.
2. **`ChatAgent("master_agent")`** -- A simple chat agent that uses the default LLM. Unlike `ReActAgent`, a `ChatAgent` does not perform tool calls -- it just passes messages to the LLM and returns the response.

### Entry Point

The `main()` coroutine creates a MAS and starts the web service with the initial query `"hello"`. The agent will respond conversationally without any system prompt being sent to the underlying model.

## Key Concepts

- **`is_disable_system_prompt`** -- A boolean flag on `HttpLLM` that strips system-role messages before API calls. Essential for models that return errors or produce degraded output when a system prompt is present.
- **ChatAgent** -- The simplest agent type in OxyGent. It forwards user messages to the LLM and returns responses without any reasoning loop or tool usage.
- **Model compatibility** -- Different LLM providers support different message formats. OxyGent provides flags like `is_disable_system_prompt` to adapt to these differences without changing agent logic.

## Expected Behavior

1. The web server starts at `http://127.0.0.1:8080`.
2. The agent receives the query "hello".
3. The LLM receives the conversation without any system prompt message.
4. The model generates a conversational response, which is displayed in the web UI.
