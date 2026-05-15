# Reset LLM Parameters Demo

**Source:** `examples/llms/demo_reset_llm_params.py`

## Overview

This example demonstrates how to reset the global LLM default parameters and override them with custom values per LLM instance. This is useful when integrating models (such as GPT-5 or other newer models) that have different default parameter requirements than what OxyGent's built-in configuration provides. The example clears global LLM config and sets specific parameters like disabling thinking mode and streaming.

## Prerequisites

- Environment variables (set in `.env` or shell):
  - `DEFAULT_LLM_API_KEY` -- API key for the LLM provider
  - `DEFAULT_LLM_BASE_URL` -- Base URL of the LLM API
  - `DEFAULT_LLM_MODEL_NAME` -- Model identifier
- Python 3.10+ with project dependencies installed

## How to Run

```bash
python -m examples.llms.demo_reset_llm_params
```

## Code Walkthrough

### Configuration

```python
Config.set_llm_config({})
```

This line resets all global LLM default parameters to an empty dictionary. By default, OxyGent's `Config` may include parameters like `temperature`, `top_p`, `stream`, etc. Clearing them ensures no unexpected defaults are sent to models that may not support them.

```python
oxy.HttpLLM(
    name="default_llm",
    ...,
    llm_params={"thinking": False, "stream": False},
)
```

After resetting the global config, instance-level `llm_params` are set explicitly. Here, `thinking` (extended thinking / chain-of-thought mode) is disabled and streaming is turned off.

### Components (`oxy_space`)

Only a single component:

1. **`HttpLLM("default_llm")`** -- An HTTP-based LLM with custom parameters and cleared global defaults.

Note that no agent is defined in this example. The LLM is called directly.

### Entry Point

The `main()` coroutine creates a MAS and calls the LLM directly using `mas.call()`:

```python
await mas.call(
    callee="default_llm",
    arguments={"messages": [{"role": "user", "content": "hello"}]},
)
```

This bypasses the agent layer entirely and sends a raw message list to the LLM, demonstrating that LLMs in OxyGent are independently callable Oxy components.

## Key Concepts

- **`Config.set_llm_config({})`** -- Resets the global LLM configuration to an empty state. This is useful when the framework's default parameters conflict with a specific model's API requirements.
- **`llm_params`** -- A dictionary of model-specific parameters passed to the LLM API. These are merged with (and override) the global config. Common parameters include `temperature`, `top_p`, `stream`, `thinking`, `max_tokens`, etc.
- **`mas.call()`** -- Directly invokes any named Oxy component (LLM, tool, or agent) without going through an agent's reasoning loop. The `callee` parameter specifies the component name, and `arguments` contains the call payload.
- **LLM as an Oxy component** -- In OxyGent, LLMs are first-class Oxy objects that can be called directly, not just through agents. This enables testing, debugging, and scripting workflows.

## Expected Behavior

1. The global LLM config is cleared.
2. The MAS initializes with a single `HttpLLM`.
3. The LLM receives the message `"hello"` with `thinking=False` and `stream=False`.
4. The response is returned directly (not streamed) and printed or logged by the framework.
