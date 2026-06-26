# LiteLLM Integration Demo

**Source:** `examples/llms/demo_litellm.py`

## Overview

This example demonstrates how to use any LLM provider through LiteLLM in OxyGent. LiteLLM is a unified interface that supports 100+ LLM providers (OpenAI, Anthropic, Google, Mistral, Cohere, and more) using a consistent API format. By using the `LiteLLM` component, you can easily switch between providers without changing the rest of your OxyGent agent setup.

## Prerequisites

- **LiteLLM** installed: `pip install litellm`
- An API key for the LLM provider you wish to use (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.), set as an environment variable or passed directly
- Python 3.10+ with project dependencies installed

**Note:** If using a LiteLLM proxy server, set the `base_url` parameter to the proxy endpoint (e.g., `http://localhost:4000`).

## How to Run

1. Install LiteLLM:
   ```bash
   pip install litellm
   ```

2. Set your API key as an environment variable (example for Anthropic):
   ```bash
   export ANTHROPIC_API_KEY="sk-..."
   ```

3. Update the `model_name` in the source code to match your desired provider and model:
   ```python
   model_name="anthropic/claude-sonnet-4-20250514",  # or "openai/gpt-4o", "gemini/gemini-pro", etc.
   ```

4. Run the example:
   ```bash
   python -m examples.llms.demo_litellm
   ```

## Code Walkthrough

### Configuration

```python
oxy.LiteLLM(
    name="default_llm",
    model_name="anthropic/claude-sonnet-4-20250514",
    # api_key="sk-...",         # or set ANTHROPIC_API_KEY env var
    # base_url="http://localhost:4000",  # optional: LiteLLM proxy
)
```

The `LiteLLM` component is configured with a `model_name` that follows LiteLLM's `provider/model` naming convention. The `api_key` can be passed directly or read from the corresponding provider environment variable. Optionally, `base_url` can point to a LiteLLM proxy server.

### Components (`oxy_space`)

Two components are defined:

1. **`LiteLLM("default_llm")`** -- A LiteLLM-based LLM that routes requests to the specified provider.
2. **`ReActAgent("agent")`** -- A reasoning-and-acting agent backed by the LiteLLM model, with a simple system prompt.

### Entry Point

The `main()` coroutine creates a MAS and calls the agent:

```python
await mas.call(
    callee="agent",
    arguments={"messages": [{"role": "user", "content": "What is 2 + 2?"}]},
)
```

This sends a user message to the ReActAgent, which uses the LiteLLM model to generate a response.

## Key Concepts

- **LiteLLM** -- A unified Python library that provides a consistent interface to 100+ LLM providers. It translates calls into each provider's native API format, so you can switch providers by changing only the `model_name`.
- **Provider/model naming** -- LiteLLM uses the `provider/model` format (e.g., `anthropic/claude-sonnet-4-20250514`, `openai/gpt-4o`, `gemini/gemini-pro`) to identify which provider and model to use.
- **LiteLLM proxy** -- Optionally, you can run a LiteLLM proxy server that centralizes API key management and load balancing. Point `base_url` to the proxy endpoint to route all requests through it.
- **Drop-in provider switching** -- Because `LiteLLM` wraps multiple providers behind a single interface, switching from one LLM provider to another requires only changing the `model_name` and API key -- no other code changes needed.

## Expected Behavior

1. The MAS initializes the `LiteLLM` component and the `ReActAgent`.
2. The user message `"What is 2 + 2?"` is sent to the agent.
3. The agent uses the LiteLLM model to reason about and answer the question.
4. The result is printed, showing the model's response (e.g., `"4"`).
